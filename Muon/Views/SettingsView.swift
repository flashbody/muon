import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var storeManager: StoreManager
    @EnvironmentObject var favoritesManager: FavoritesManager
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var soundSettings: SoundSettings
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                List {
                    // Premium Status
                    Section("Premium") {
                        HStack {
                            Image(systemName: storeManager.isPurchased ? "checkmark.seal.fill" : "lock.fill")
                                .foregroundColor(storeManager.isPurchased ? .green : .orange)
                            Text(storeManager.isPurchased ? "Premium Unlocked" : "Free Version")
                                .foregroundColor(.white)
                            Spacer()
                            if !storeManager.isPurchased {
                                Text("Upgrade")
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.cyan)
                            }
                        }
                        
                        if !storeManager.isPurchased {
                            Button("Restore Purchase") {
                                Task { await storeManager.restore() }
                            }
                            .foregroundColor(.cyan)
                        }
                    }
                    
                    // Saved Presets
                    if storeManager.isPurchased && !favoritesManager.presets.isEmpty {
                        Section("Saved Mixes") {
                            ForEach(favoritesManager.presets) { preset in
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(preset.name)
                                            .foregroundColor(.white)
                                        Text("\(preset.items.count) sounds")
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                    }
                                    Spacer()
                                    Button(action: {
                                        soundMixer.applyPreset(preset)
                                        dismiss()
                                    }) {
                                        Image(systemName: "play.circle.fill")
                                            .foregroundColor(.cyan)
                                    }
                                }
                            }
                            .onDelete { indexSet in
                                for index in indexSet {
                                    favoritesManager.deletePreset(favoritesManager.presets[index])
                                }
                            }
                        }
                    }
                    
                    // Sound Settings
                    Section("Sound Settings") {
                        Toggle(isOn: $soundSettings.useRealSound) {
                            HStack {
                                Image(systemName: "waveform")
                                    .foregroundColor(.cyan)
                                Text(soundSettings.useRealSound ? "Real Recordings" : "Algorithm Generated")
                                    .foregroundColor(.white)
                            }
                        }
                        .tint(.cyan)
                        
                        if soundSettings.useRealSound {
                            Text("⚠️ Real recordings not yet available for all sounds. Algorithm versions will be used as fallback.")
                                .font(.system(size: 11))
                                .foregroundColor(.gray)
                        }
                    }
                    
                    // About
                    Section("About") {
                        HStack {
                            Text("Version")
                                .foregroundColor(.white)
                            Spacer()
                            Text("1.0.0")
                                .foregroundColor(.gray)
                        }
                    }
                    
                    // Licenses
                    Section("Audio Licenses") {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("All audio content in this app is algorithmically generated — no copyrighted music compositions are used.")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                            
                            Text("Sources:")
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(.white.opacity(0.7))
                            
                            Text("• Algorithmically generated audio (owned by Weaveon)")
                                .font(.system(size: 11))
                                .foregroundColor(.gray)
                            
                            Text("• Pixabay.com — Pixabay Content License (free commercial use, for future updates)")
                                .font(.system(size: 11))
                                .foregroundColor(.gray)
                        }
                        .padding(.vertical, 4)
                    }
                    
                    // Legal
                    Section("Legal") {
                        Link("Privacy Policy", destination: URL(string: "https://weaveon.github.io/muon/privacy")!)
                            .foregroundColor(.cyan)
                        Link("Terms of Use", destination: URL(string: "https://weaveon.github.io/muon/terms")!)
                            .foregroundColor(.cyan)
                    }
                }
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                        .foregroundColor(.cyan)
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}
