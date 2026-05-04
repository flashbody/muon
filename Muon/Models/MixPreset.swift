import Foundation

struct MixPreset: Identifiable, Codable {
    let id: UUID
    var name: String
    var items: [MixItem]
    let createdAt: Date
    
    struct MixItem: Codable, Hashable {
        let soundId: String
        var volume: Float
    }
    
    init(name: String, items: [MixItem]) {
        self.id = UUID()
        self.name = name
        self.items = items
        self.createdAt = Date()
    }
}
