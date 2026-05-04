import SwiftUI

struct SoundCardView: View {
    let sound: Sound
    let onTap: () -> Void
    
    @EnvironmentObject var soundMixer: SoundMixer
    
    private var isActive: Bool {
        soundMixer.isSoundActive(sound)
    }
    
    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 10) {
                Text(sound.emoji)
                    .font(.system(size: 32))
                
                Text(sound.name)
                    .font(.system(size: 13, weight: .medium, design: .rounded))
                    .foregroundColor(isActive ? .white : .gray.opacity(0.8))
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(isActive ? cardActiveGradient : cardInactiveGradient)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(isActive ? Color.cyan.opacity(0.5) : Color.white.opacity(0.06), lineWidth: 1)
            )
            .scaleEffect(isActive ? 1.02 : 1.0)
        }
        .buttonStyle(SoundCardButtonStyle())
        .animation(.easeInOut(duration: 0.2), value: isActive)
    }
    
    private var cardActiveGradient: LinearGradient {
        LinearGradient(
            colors: [Color.cyan.opacity(0.2), Color.blue.opacity(0.15)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    private var cardInactiveGradient: LinearGradient {
        LinearGradient(
            colors: [Color.white.opacity(0.05), Color.white.opacity(0.02)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}

struct SoundCardButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}
