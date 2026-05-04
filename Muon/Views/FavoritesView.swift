import SwiftUI

struct FavoritesView: View {
    @EnvironmentObject var favoritesManager: FavoritesManager
    @EnvironmentObject var soundMixer: SoundMixer
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                if favoritesManager.presets.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 40))
                            .foregroundColor(.gray.opacity(0.5))
                        Text("No saved mixes yet")
                            .font(.system(size: 16))
                            .foregroundColor(.gray)
                        Text("Play a mix and tap the heart to save")
                            .font(.system(size: 13))
                            .foregroundColor(.gray.opacity(0.7))
                    }
                } else {
                    List {
                        ForEach(favoritesManager.presets) { preset in
                            Button(action: {
                                soundMixer.applyPreset(preset)
                                dismiss()
                            }) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(preset.name)
                                            .font(.system(size: 15, weight: .medium))
                                            .foregroundColor(.white)
                                        
                                        HStack(spacing: 4) {
                                            ForEach(preset.items, id: \.soundId) { item in
                                                if let sound = Sound.allSounds.first(where: { $0.id == item.soundId }) {
                                                    Text(sound.emoji)
                                                        .font(.system(size: 14))
                                                }
                                            }
                                        }
                                    }
                                    
                                    Spacer()
                                    
                                    Image(systemName: "play.circle.fill")
                                        .font(.system(size: 22))
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
                    .scrollContentBackground(.hidden)
                }
            }
            .navigationTitle("Saved Mixes")
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
