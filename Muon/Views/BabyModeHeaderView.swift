import SwiftUI

struct BabyModeHeaderView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "heart.fill")
                    .foregroundColor(.pink.opacity(0.8))
                Text("Baby Soothe")
                    .font(.system(size: 16, weight: .semibold, design: .rounded))
                    .foregroundColor(.white)
            }
            
            Text("Womb-like sounds that trigger your newborn's calming reflex. The same sounds they heard for 9 months.")
                .font(.system(size: 12))
                .foregroundColor(.gray)
                .lineLimit(3)
            
            // Recommended combos
            VStack(spacing: 6) {
                RecommendedComboRow(
                    emoji: "💓+🫀",
                    name: "Womb Simulation",
                    description: "Heartbeat + Blood Flow"
                )
                RecommendedComboRow(
                    emoji: "🤫+〰️",
                    name: "Calming Reflex",
                    description: "Shushing + Pink Noise"
                )
            }
            .padding(.top, 4)
        }
        .padding(14)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.pink.opacity(0.05))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.pink.opacity(0.15), lineWidth: 1)
                )
        )
    }
}

struct RecommendedComboRow: View {
    let emoji: String
    let name: String
    let description: String
    
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var storeManager: StoreManager
    
    var body: some View {
        HStack {
            Text(emoji)
                .font(.system(size: 14))
            
            VStack(alignment: .leading, spacing: 1) {
                Text(name)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.9))
                Text(description)
                    .font(.system(size: 10))
                    .foregroundColor(.gray)
            }
            
            Spacer()
            
            Image(systemName: "play.circle.fill")
                .font(.system(size: 18))
                .foregroundColor(.pink.opacity(0.6))
        }
        .padding(.vertical, 4)
    }
}
