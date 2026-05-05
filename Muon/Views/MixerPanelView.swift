import SwiftUI

struct MixerPanelView: View {
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var storeManager: StoreManager
    @Binding var showSavePreset: Bool
    
    var body: some View {
        VStack(spacing: 12) {
            // Drag indicator
            RoundedRectangle(cornerRadius: 2)
                .fill(Color.gray.opacity(0.4))
                .frame(width: 36, height: 4)
                .padding(.top, 8)
            
            // Header
            HStack {
                Text("Now Playing")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundColor(.white.opacity(0.8))
                
                Text("(\(soundMixer.activeCount)/4)")
                    .font(.system(size: 12))
                    .foregroundColor(.gray)
                
                Spacer()
                
                // Save preset button
                if storeManager.isPurchased {
                    Button(action: { showSavePreset = true }) {
                        Image(systemName: "heart.circle")
                            .font(.system(size: 20))
                            .foregroundColor(.pink.opacity(0.8))
                    }
                    .padding(.trailing, 4)
                }
                
                // Stop all button
                Button(action: { soundMixer.stopAll() }) {
                    Image(systemName: "stop.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.red.opacity(0.7))
                }
            }
            .padding(.horizontal, 16)
            
            // Volume sliders for each active sound
            ForEach(Array(soundMixer.activeSounds.keys.sorted()), id: \.self) { soundId in
                if let sound = Sound.allSounds.first(where: { $0.id == soundId }),
                   let volume = soundMixer.activeSounds[soundId] {
                    MixerSliderRow(sound: sound, volume: volume)
                }
            }
            
            Spacer().frame(height: 8)
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color(white: 0.1))
                .shadow(color: .black.opacity(0.5), radius: 10, y: -5)
        )
    }
}

struct MixerSliderRow: View {
    let sound: Sound
    let volume: Float
    
    @EnvironmentObject var soundMixer: SoundMixer
    @State private var sliderValue: Float = 0.7
    
    var body: some View {
        HStack(spacing: 10) {
            Text(sound.emoji)
                .font(.system(size: 18))
                .frame(width: 28)
            
            Text(sound.name)
                .font(.system(size: 12, design: .rounded))
                .foregroundColor(.gray)
                .frame(width: 80, alignment: .leading)
                .lineLimit(1)
            
            Slider(value: $sliderValue, in: 0...1) { editing in
                if !editing {
                    soundMixer.setVolume(for: sound.id, volume: sliderValue)
                }
            }
            .tint(.cyan)
            .onChange(of: sliderValue) { _, newValue in
                soundMixer.setVolume(for: sound.id, volume: newValue)
            }
            
            Text("\(Int(sliderValue * 100))%")
                .font(.system(size: 11, design: .monospaced))
                .foregroundColor(.gray)
                .frame(width: 35)
        }
        .padding(.horizontal, 16)
        .onAppear {
            sliderValue = volume
        }
    }
}
