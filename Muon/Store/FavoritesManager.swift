import Foundation

/// 收藏组合管理器
final class FavoritesManager: ObservableObject {
    
    @Published var presets: [MixPreset] = []
    
    private let storageKey = "muon_favorites"
    
    init() {
        loadPresets()
    }
    
    func savePreset(name: String, items: [MixPreset.MixItem]) {
        let preset = MixPreset(name: name, items: items)
        presets.append(preset)
        persistPresets()
    }
    
    func deletePreset(_ preset: MixPreset) {
        presets.removeAll { $0.id == preset.id }
        persistPresets()
    }
    
    func renamePreset(_ preset: MixPreset, newName: String) {
        if let index = presets.firstIndex(where: { $0.id == preset.id }) {
            presets[index].name = newName
            persistPresets()
        }
    }
    
    // MARK: - Persistence
    
    private func persistPresets() {
        if let data = try? JSONEncoder().encode(presets) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
    
    private func loadPresets() {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let saved = try? JSONDecoder().decode([MixPreset].self, from: data) else {
            return
        }
        presets = saved
    }
}
