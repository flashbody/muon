import Foundation

/// 用户记忆管理器 - 记住用户上次的播放状态，下次打开自动恢复
final class UserMemory: ObservableObject {
    
    private let lastSessionKey = "muon_last_session"
    private let lastCategoryKey = "muon_last_category"
    private let launchCountKey = "muon_launch_count"
    private let hasSeenOnboardingKey = "muon_has_seen_onboarding"
    
    @Published var lastSession: SessionSnapshot?
    @Published var launchCount: Int = 0
    @Published var hasSeenOnboarding: Bool = false
    
    /// 上次播放会话的快照
    struct SessionSnapshot: Codable {
        let items: [MixPreset.MixItem]
        let category: String
        let timestamp: Date
    }
    
    init() {
        loadMemory()
        incrementLaunchCount()
    }
    
    // MARK: - Save Session
    
    /// 保存当前播放状态（App进入后台或退出时调用）
    func saveSession(activeSounds: [String: Float], currentCategory: String) {
        guard !activeSounds.isEmpty else {
            clearSession()
            return
        }
        
        let items = activeSounds.map { MixPreset.MixItem(soundId: $0.key, volume: $0.value) }
        let snapshot = SessionSnapshot(
            items: items,
            category: currentCategory,
            timestamp: Date()
        )
        
        if let data = try? JSONEncoder().encode(snapshot) {
            UserDefaults.standard.set(data, forKey: lastSessionKey)
        }
        
        lastSession = snapshot
    }
    
    /// 加载上次的播放状态
    func loadLastSession() -> SessionSnapshot? {
        guard let data = UserDefaults.standard.data(forKey: lastSessionKey),
              let snapshot = try? JSONDecoder().decode(SessionSnapshot.self, from: data) else {
            return nil
        }
        
        // 只恢复7天内的会话
        let sevenDaysAgo = Date().addingTimeInterval(-7 * 24 * 3600)
        guard snapshot.timestamp > sevenDaysAgo else {
            clearSession()
            return nil
        }
        
        return snapshot
    }
    
    func clearSession() {
        UserDefaults.standard.removeObject(forKey: lastSessionKey)
        lastSession = nil
    }
    
    // MARK: - Category Memory
    
    func saveLastCategory(_ category: String) {
        UserDefaults.standard.set(category, forKey: lastCategoryKey)
    }
    
    func loadLastCategory() -> String? {
        UserDefaults.standard.string(forKey: lastCategoryKey)
    }
    
    // MARK: - Launch Count
    
    private func incrementLaunchCount() {
        launchCount = UserDefaults.standard.integer(forKey: launchCountKey) + 1
        UserDefaults.standard.set(launchCount, forKey: launchCountKey)
    }
    
    // MARK: - Onboarding
    
    func markOnboardingSeen() {
        hasSeenOnboarding = true
        UserDefaults.standard.set(true, forKey: hasSeenOnboardingKey)
    }
    
    // MARK: - Private
    
    private func loadMemory() {
        hasSeenOnboarding = UserDefaults.standard.bool(forKey: hasSeenOnboardingKey)
        lastSession = loadLastSession()
        launchCount = UserDefaults.standard.integer(forKey: launchCountKey)
    }
}
