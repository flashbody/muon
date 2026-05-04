import Foundation
import Combine

/// 睡眠定时器 - 倒计时到0后渐弱停止音频
final class SleepTimer: ObservableObject {
    
    @Published var isActive: Bool = false
    @Published var remainingSeconds: Int = 0
    @Published var selectedMinutes: Int = 30
    
    private var timer: Timer?
    private var onComplete: (() -> Void)?
    
    static let presetMinutes = [15, 30, 45, 60, 90, 120]
    
    var remainingFormatted: String {
        let hours = remainingSeconds / 3600
        let minutes = (remainingSeconds % 3600) / 60
        let seconds = remainingSeconds % 60
        
        if hours > 0 {
            return String(format: "%d:%02d:%02d", hours, minutes, seconds)
        } else {
            return String(format: "%02d:%02d", minutes, seconds)
        }
    }
    
    func start(minutes: Int, onComplete: @escaping () -> Void) {
        stop()
        
        self.selectedMinutes = minutes
        self.remainingSeconds = minutes * 60
        self.onComplete = onComplete
        self.isActive = true
        
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            
            DispatchQueue.main.async {
                if self.remainingSeconds > 0 {
                    self.remainingSeconds -= 1
                } else {
                    self.onComplete?()
                    self.stop()
                }
            }
        }
    }
    
    func stop() {
        timer?.invalidate()
        timer = nil
        isActive = false
        remainingSeconds = 0
        onComplete = nil
    }
    
    func addTime(minutes: Int) {
        remainingSeconds += minutes * 60
    }
    
    deinit {
        timer?.invalidate()
    }
}
