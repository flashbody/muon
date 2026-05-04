import SwiftUI

@main
struct MuonApp: App {
    @StateObject private var soundMixer = SoundMixer()
    @StateObject private var storeManager = StoreManager()
    @StateObject private var sleepTimer = SleepTimer()
    @StateObject private var favoritesManager = FavoritesManager()
    @StateObject private var userMemory = UserMemory()
    
    @State private var showLaunchAnimation = true
    
    @Environment(\.scenePhase) private var scenePhase
    
    var body: some Scene {
        WindowGroup {
            Group {
                if showLaunchAnimation {
                    LaunchAnimationView {
                        withAnimation(.easeIn(duration: 0.2)) {
                            showLaunchAnimation = false
                        }
                        restoreLastSession()
                    }
                } else {
                    ContentView()
                        .environmentObject(soundMixer)
                        .environmentObject(storeManager)
                        .environmentObject(sleepTimer)
                        .environmentObject(favoritesManager)
                        .environmentObject(userMemory)
                }
            }
            .preferredColorScheme(.dark)
        }
    }
    
    // MARK: - Scene Phase Handling (Background Support)
    
    private func handleScenePhase(_ phase: ScenePhase) {
        switch phase {
        case .background:
            // Save current session when going to background
            saveCurrentSession()
            
            // Update Now Playing info for lock screen
            if soundMixer.isPlaying {
                let activeNames = soundMixer.activeSounds.keys.compactMap { id in
                    Sound.allSounds.first(where: { $0.id == id })?.name
                }.joined(separator: " + ")
                NowPlayingManager.shared.updateNowPlaying(
                    title: activeNames.isEmpty ? "Muon" : activeNames,
                    isPlaying: true
                )
            }
            
        case .active:
            // Refresh audio session when becoming active
            break
            
        case .inactive:
            break
            
        @unknown default:
            break
        }
    }
    
    // MARK: - User Memory
    
    private func saveCurrentSession() {
        userMemory.saveSession(
            activeSounds: soundMixer.activeSounds,
            currentCategory: "" // Will be set from ContentView
        )
    }
    
    private func restoreLastSession() {
        guard let session = userMemory.loadLastSession() else { return }
        
        // Restore with a slight delay to ensure audio engine is ready
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            for item in session.items {
                if let sound = Sound.allSounds.first(where: { $0.id == item.soundId }) {
                    // For free users, only restore 1 sound
                    if !storeManager.isPurchased && soundMixer.activeCount >= 1 {
                        break
                    }
                    soundMixer.playSound(sound)
                    soundMixer.setVolume(for: sound.id, volume: item.volume)
                }
            }
        }
    }
}
