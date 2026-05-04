import SwiftUI

struct TimerView: View {
    @EnvironmentObject var soundMixer: SoundMixer
    @EnvironmentObject var sleepTimer: SleepTimer
    @Environment(\.dismiss) private var dismiss
    
    @State private var selectedMinutes: Int = 30
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                VStack(spacing: 32) {
                    // Current timer display
                    if sleepTimer.isActive {
                        activeTimerView
                    } else {
                        timerSelector
                    }
                }
                .padding()
            }
            .navigationTitle("Sleep Timer")
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
    
    // MARK: - Active Timer View
    
    private var activeTimerView: some View {
        VStack(spacing: 24) {
            Text(sleepTimer.remainingFormatted)
                .font(.system(size: 56, weight: .ultraLight, design: .monospaced))
                .foregroundColor(.cyan)
            
            Text("Audio will fade out gently")
                .font(.system(size: 14))
                .foregroundColor(.gray)
            
            HStack(spacing: 16) {
                Button(action: { sleepTimer.addTime(minutes: 15) }) {
                    Text("+15 min")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.white.opacity(0.1))
                        .cornerRadius(20)
                }
                
                Button(action: { sleepTimer.stop() }) {
                    Text("Cancel")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.red.opacity(0.8))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(20)
                }
            }
        }
    }
    
    // MARK: - Timer Selector
    
    private var timerSelector: some View {
        VStack(spacing: 24) {
            Image(systemName: "moon.zzz.fill")
                .font(.system(size: 48))
                .foregroundColor(.cyan.opacity(0.6))
            
            Text("Set Sleep Timer")
                .font(.system(size: 20, weight: .medium, design: .rounded))
                .foregroundColor(.white)
            
            Text("Audio will gradually fade out when the timer ends")
                .font(.system(size: 14))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            // Time options
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                ForEach(SleepTimer.presetMinutes, id: \.self) { minutes in
                    Button(action: { selectedMinutes = minutes }) {
                        Text(formatMinutes(minutes))
                            .font(.system(size: 15, weight: .medium))
                            .foregroundColor(selectedMinutes == minutes ? .black : .white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 48)
                            .background(
                                selectedMinutes == minutes ?
                                Color.cyan : Color.white.opacity(0.08)
                            )
                            .cornerRadius(12)
                    }
                }
            }
            .padding(.top, 8)
            
            // Start button
            Button(action: startTimer) {
                Text("Start Timer")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.cyan)
                    .cornerRadius(14)
            }
            .padding(.top, 8)
            .disabled(!soundMixer.isPlaying)
            .opacity(soundMixer.isPlaying ? 1.0 : 0.4)
            
            if !soundMixer.isPlaying {
                Text("Play a sound first")
                    .font(.system(size: 12))
                    .foregroundColor(.gray)
            }
        }
    }
    
    // MARK: - Helpers
    
    private func startTimer() {
        sleepTimer.start(minutes: selectedMinutes) {
            soundMixer.fadeOutAndStop(duration: 10)
        }
        dismiss()
    }
    
    private func formatMinutes(_ minutes: Int) -> String {
        if minutes >= 60 {
            let h = minutes / 60
            let m = minutes % 60
            return m > 0 ? "\(h)h \(m)m" : "\(h) hr"
        }
        return "\(minutes) min"
    }
}
