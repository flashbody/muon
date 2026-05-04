import SwiftUI

struct SavePresetView: View {
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var favoritesManager: FavoritesManager
    @Environment(\.dismiss) private var dismiss
    
    @State private var presetName: String = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                VStack(spacing: 24) {
                    Image(systemName: "heart.circle.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.pink.opacity(0.7))
                    
                    Text("Save Current Mix")
                        .font(.system(size: 20, weight: .medium, design: .rounded))
                        .foregroundColor(.white)
                    
                    // Show current sounds
                    VStack(spacing: 8) {
                        ForEach(Array(soundMixer.activeSounds.keys.sorted()), id: \.self) { soundId in
                            if let sound = Sound.allSounds.first(where: { $0.id == soundId }) {
                                HStack {
                                    Text(sound.emoji)
                                    Text(sound.name)
                                        .font(.system(size: 14))
                                        .foregroundColor(.white.opacity(0.8))
                                    Spacer()
                                    if let vol = soundMixer.activeSounds[soundId] {
                                        Text("\(Int(vol * 100))%")
                                            .font(.system(size: 12))
                                            .foregroundColor(.gray)
                                    }
                                }
                            }
                        }
                    }
                    .padding()
                    .background(Color.white.opacity(0.05))
                    .cornerRadius(12)
                    
                    // Name input
                    TextField("Mix name", text: $presetName)
                        .textFieldStyle(.plain)
                        .padding()
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(12)
                        .foregroundColor(.white)
                    
                    // Save button
                    Button(action: savePreset) {
                        Text("Save")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.black)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(presetName.isEmpty ? Color.gray : Color.cyan)
                            .cornerRadius(14)
                    }
                    .disabled(presetName.isEmpty)
                    
                    Spacer()
                }
                .padding(24)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(.gray)
                }
            }
        }
        .preferredColorScheme(.dark)
    }
    
    private func savePreset() {
        let items = soundMixer.currentMixItems()
        favoritesManager.savePreset(name: presetName, items: items)
        dismiss()
    }
}
