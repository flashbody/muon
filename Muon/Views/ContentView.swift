import SwiftUI

struct ContentView: View {
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var storeManager: StoreManager
    @EnvironmentObject var sleepTimer: SleepTimer
    @EnvironmentObject var userMemory: UserMemory
    
    @State private var selectedCategory: SoundCategory = .water
    @State private var showTimer: Bool = false
    @State private var showSettings: Bool = false
    @State private var showPaywall: Bool = false
    @State private var showSavePreset: Bool = false
    @State private var showResumeBanner: Bool = false
    
    @Environment(\.scenePhase) private var scenePhase
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Resume banner (shows when there's a previous session)
                if showResumeBanner {
                    resumeBanner
                        .transition(.move(edge: .top).combined(with: .opacity))
                }
                
                // Top Bar
                topBar
                
                // Category Tabs
                categoryTabs
                
                // Sound Grid
                soundGrid
                
                // Mixer Panel (shown when sounds are active)
                if !soundMixer.activeSounds.isEmpty {
                    MixerPanelView(showSavePreset: $showSavePreset)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                }
            }
            .navigationBarHidden(true)
            .background(Color.black)
        }
        .animation(.easeInOut(duration: 0.3), value: soundMixer.activeSounds.isEmpty)
        .animation(.easeInOut(duration: 0.3), value: showResumeBanner)
        .sheet(isPresented: $showTimer) {
            TimerView()
        }
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .sheet(isPresented: $showPaywall) {
            PaywallView()
        }
        .sheet(isPresented: $showSavePreset) {
            SavePresetView()
        }
        .onAppear {
            restoreCategory()
        }
        .onChange(of: selectedCategory) { newValue in
            userMemory.saveLastCategory(newValue.rawValue)
        }
        .onChange(of: scenePhase) { newPhase in
            if newPhase == .background {
                userMemory.saveSession(
                    activeSounds: soundMixer.activeSounds,
                    currentCategory: selectedCategory.rawValue
                )
                
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
            }
        }
    }
    
    // MARK: - Resume Banner
    
    private var resumeBanner: some View {
        HStack {
            Image(systemName: "arrow.counterclockwise.circle.fill")
                .foregroundColor(.cyan)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("Resume last session?")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white)
                
                if let session = userMemory.lastSession {
                    let names = session.items.prefix(3).compactMap { item in
                        Sound.allSounds.first(where: { $0.id == item.soundId })?.emoji
                    }.joined(separator: " ")
                    Text(names)
                        .font(.system(size: 11))
                        .foregroundColor(.gray)
                }
            }
            
            Spacer()
            
            Button("Resume") {
                resumeLastSession()
            }
            .font(.system(size: 13, weight: .semibold))
            .foregroundColor(.black)
            .padding(.horizontal, 14)
            .padding(.vertical, 6)
            .background(Color.cyan)
            .cornerRadius(16)
            
            Button(action: { dismissResumeBanner() }) {
                Image(systemName: "xmark")
                    .font(.system(size: 12))
                    .foregroundColor(.gray)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.05))
    }
    
    // MARK: - Top Bar
    
    private var topBar: some View {
        HStack {
            Text("Muon")
                .font(.system(size: 28, weight: .light, design: .rounded))
                .foregroundColor(.white)
            
            Spacer()
            
            // Timer button
            Button(action: { showTimer = true }) {
                HStack(spacing: 4) {
                    Image(systemName: "moon.zzz")
                        .font(.system(size: 18))
                    if sleepTimer.isActive {
                        Text(sleepTimer.remainingFormatted)
                            .font(.system(size: 12, design: .monospaced))
                    }
                }
                .foregroundColor(sleepTimer.isActive ? .cyan : .gray)
            }
            .padding(.trailing, 8)
            
            // Settings button
            Button(action: { showSettings = true }) {
                Image(systemName: "gearshape")
                    .font(.system(size: 18))
                    .foregroundColor(.gray)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 4)
        .padding(.bottom, 8)
    }
    
    // MARK: - Category Tabs
    
    private var categoryTabs: some View {
        HStack(spacing: 0) {
            ForEach(SoundCategory.allCases) { category in
                Button(action: { selectedCategory = category }) {
                    VStack(spacing: 6) {
                        Image(systemName: category.icon)
                            .font(.system(size: 16))
                        Text(category.displayName)
                            .font(.system(size: 12, weight: .medium))
                    }
                    .foregroundColor(selectedCategory == category ? .white : .gray.opacity(0.6))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        selectedCategory == category ?
                        Color.white.opacity(0.08) : Color.clear
                    )
                    .cornerRadius(10)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }
    
    // MARK: - Sound Grid
    
    private var soundGrid: some View {
        ScrollView {
            if selectedCategory == .baby {
                BabyModeHeaderView()
                    .padding(.horizontal, 16)
                    .padding(.bottom, 8)
            }
            
            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: 12),
                GridItem(.flexible(), spacing: 12)
            ], spacing: 12) {
                ForEach(Sound.sounds(for: selectedCategory)) { sound in
                    SoundCardView(sound: sound) {
                        handleSoundTap(sound)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, soundMixer.activeSounds.isEmpty ? 16 : 180)
        }
    }
    
    // MARK: - Logic
    
    private func handleSoundTap(_ sound: Sound) {
        if soundMixer.isSoundActive(sound) {
            soundMixer.stopSound(sound)
        } else {
            if soundMixer.activeCount >= 1 && !storeManager.isPurchased {
                showPaywall = true
                return
            }
            if soundMixer.canAddMore {
                soundMixer.playSound(sound)
            }
        }
    }
    
    // MARK: - User Memory
    
    private func restoreCategory() {
        if let catString = userMemory.loadLastCategory(),
           let category = SoundCategory(rawValue: catString) {
            selectedCategory = category
        }
        
        // Show resume banner if there's a previous session and nothing is playing
        if userMemory.loadLastSession() != nil && soundMixer.activeSounds.isEmpty {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                showResumeBanner = true
            }
        }
    }
    
    private func resumeLastSession() {
        guard let session = userMemory.loadLastSession() else { return }
        
        for item in session.items {
            if let sound = Sound.allSounds.first(where: { $0.id == item.soundId }) {
                if !storeManager.isPurchased && soundMixer.activeCount >= 1 { break }
                soundMixer.playSound(sound)
                soundMixer.setVolume(for: sound.id, volume: item.volume)
            }
        }
        
        dismissResumeBanner()
    }
    
    private func dismissResumeBanner() {
        showResumeBanner = false
        userMemory.clearSession()
    }
}

#Preview {
    ContentView()
        .environmentObject(SoundMixer())
        .environmentObject(StoreManager())
        .environmentObject(SleepTimer())
        .environmentObject(FavoritesManager())
        .environmentObject(UserMemory())
}
