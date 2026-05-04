import Foundation
import AVFoundation
import Combine

/// 核心音频引擎 - 管理多音轨并行播放
final class SoundMixer: ObservableObject {
    
    private var audioEngine = AVAudioEngine()
    private var playerNodes: [String: AVAudioPlayerNode] = [:]
    private var audioBuffers: [String: AVAudioPCMBuffer] = [:]
    
    @Published var activeSounds: [String: Float] = [:] // soundId: volume (0.0-1.0)
    @Published var isPlaying: Bool = false
    
    private let maxSimultaneous = 4
    
    init() {
        setupAudioSession()
    }
    
    // MARK: - Audio Session
    
    private func setupAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .default, options: [.mixWithOthers])
            try session.setActive(true)
        } catch {
            print("Audio session setup failed: \(error)")
        }
    }
    
    // MARK: - Play / Stop
    
    func toggleSound(_ sound: Sound) {
        if activeSounds[sound.id] != nil {
            stopSound(sound)
        } else {
            playSound(sound)
        }
    }
    
    func playSound(_ sound: Sound) {
        guard activeSounds.count < maxSimultaneous else { return }
        guard activeSounds[sound.id] == nil else { return }
        
        // Load buffer if not cached
        if audioBuffers[sound.id] == nil {
            guard let buffer = loadAudioBuffer(for: sound) else { return }
            audioBuffers[sound.id] = buffer
        }
        
        guard let buffer = audioBuffers[sound.id] else { return }
        
        // Create player node
        let playerNode = AVAudioPlayerNode()
        audioEngine.attach(playerNode)
        audioEngine.connect(playerNode, to: audioEngine.mainMixerNode, format: buffer.format)
        
        playerNodes[sound.id] = playerNode
        activeSounds[sound.id] = 0.7 // Default volume 70%
        
        // Start engine if needed
        if !audioEngine.isRunning {
            do {
                try audioEngine.start()
            } catch {
                print("Engine start failed: \(error)")
                return
            }
        }
        
        // Schedule buffer looping and play
        playerNode.scheduleBuffer(buffer, at: nil, options: .loops)
        playerNode.play()
        playerNode.volume = 0.7
        
        isPlaying = true
    }
    
    func stopSound(_ sound: Sound) {
        guard let playerNode = playerNodes[sound.id] else { return }
        
        playerNode.stop()
        audioEngine.detach(playerNode)
        
        playerNodes.removeValue(forKey: sound.id)
        activeSounds.removeValue(forKey: sound.id)
        
        if activeSounds.isEmpty {
            audioEngine.stop()
            isPlaying = false
        }
    }
    
    func stopAll() {
        for (id, node) in playerNodes {
            node.stop()
            audioEngine.detach(node)
            playerNodes.removeValue(forKey: id)
        }
        activeSounds.removeAll()
        audioEngine.stop()
        isPlaying = false
    }
    
    // MARK: - Volume Control
    
    func setVolume(for soundId: String, volume: Float) {
        guard let playerNode = playerNodes[soundId] else { return }
        playerNode.volume = volume
        activeSounds[soundId] = volume
    }
    
    // MARK: - Fade Out
    
    func fadeOutAndStop(duration: TimeInterval = 10.0) {
        let steps = 50
        let interval = duration / Double(steps)
        let currentVolumes = activeSounds
        
        for step in 0..<steps {
            DispatchQueue.main.asyncAfter(deadline: .now() + interval * Double(step)) { [weak self] in
                guard let self = self else { return }
                let factor = Float(1.0 - Double(step + 1) / Double(steps))
                for (id, originalVolume) in currentVolumes {
                    self.setVolume(for: id, volume: originalVolume * factor)
                }
            }
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) { [weak self] in
            self?.stopAll()
        }
    }
    
    // MARK: - Preset Support
    
    func applyPreset(_ preset: MixPreset) {
        stopAll()
        for item in preset.items {
            if let sound = Sound.allSounds.first(where: { $0.id == item.soundId }) {
                playSound(sound)
                setVolume(for: sound.id, volume: item.volume)
            }
        }
    }
    
    func currentMixItems() -> [MixPreset.MixItem] {
        activeSounds.map { MixPreset.MixItem(soundId: $0.key, volume: $0.value) }
    }
    
    // MARK: - Check State
    
    func isSoundActive(_ sound: Sound) -> Bool {
        activeSounds[sound.id] != nil
    }
    
    var activeCount: Int {
        activeSounds.count
    }
    
    var canAddMore: Bool {
        activeSounds.count < maxSimultaneous
    }
    
    // MARK: - Audio Buffer Loading
    
    private func loadAudioBuffer(for sound: Sound) -> AVAudioPCMBuffer? {
        guard let url = Bundle.main.url(forResource: sound.fileName, withExtension: "m4a") else {
            print("Audio file not found: \(sound.fileName).m4a")
            return nil
        }
        
        do {
            let audioFile = try AVAudioFile(forReading: url)
            let format = audioFile.processingFormat
            let frameCount = AVAudioFrameCount(audioFile.length)
            
            guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount) else {
                return nil
            }
            
            try audioFile.read(into: buffer)
            return buffer
        } catch {
            print("Failed to load audio: \(error)")
            return nil
        }
    }
}
