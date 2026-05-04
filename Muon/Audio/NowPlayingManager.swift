import Foundation
import MediaPlayer

/// 管理控制中心Now Playing信息和远程控制
final class NowPlayingManager {
    
    static let shared = NowPlayingManager()
    
    private init() {
        setupRemoteControls()
    }
    
    func updateNowPlaying(title: String, isPlaying: Bool) {
        var nowPlayingInfo = [String: Any]()
        nowPlayingInfo[MPMediaItemPropertyTitle] = title
        nowPlayingInfo[MPMediaItemPropertyArtist] = "Muon"
        nowPlayingInfo[MPNowPlayingInfoPropertyPlaybackRate] = isPlaying ? 1.0 : 0.0
        
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo
    }
    
    func clearNowPlaying() {
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nil
    }
    
    private func setupRemoteControls() {
        let commandCenter = MPRemoteCommandCenter.shared()
        
        commandCenter.playCommand.isEnabled = true
        commandCenter.pauseCommand.isEnabled = true
        commandCenter.togglePlayPauseCommand.isEnabled = true
        
        // These will be connected from the view layer
        commandCenter.playCommand.addTarget { _ in .success }
        commandCenter.pauseCommand.addTarget { _ in .success }
    }
    
    func setupPlayPauseHandlers(onPlay: @escaping () -> Void, onPause: @escaping () -> Void) {
        let commandCenter = MPRemoteCommandCenter.shared()
        
        commandCenter.playCommand.removeTarget(nil)
        commandCenter.pauseCommand.removeTarget(nil)
        commandCenter.togglePlayPauseCommand.removeTarget(nil)
        
        commandCenter.playCommand.addTarget { _ in
            onPlay()
            return .success
        }
        
        commandCenter.pauseCommand.addTarget { _ in
            onPause()
            return .success
        }
        
        commandCenter.togglePlayPauseCommand.addTarget { _ in
            onPlay() // Toggle handled externally
            return .success
        }
    }
}
