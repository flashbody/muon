import Foundation

enum SoundCategory: String, CaseIterable, Identifiable {
    case water = "Water"
    case nature = "Nature"
    case indoor = "Indoor"
    case baby = "Baby"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .water: return "Water"
        case .nature: return "Nature"
        case .indoor: return "Indoor"
        case .baby: return "Baby"
        }
    }
    
    var icon: String {
        switch self {
        case .water: return "drop.fill"
        case .nature: return "leaf.fill"
        case .indoor: return "house.fill"
        case .baby: return "heart.fill"
        }
    }
}

struct Sound: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let fileName: String
    let category: String
    let emoji: String
    
    var categoryEnum: SoundCategory {
        SoundCategory(rawValue: category) ?? .nature
    }
}

extension Sound {
    static let allSounds: [Sound] = [
        // Water
        Sound(id: "light_rain", name: "Light Rain", fileName: "water_light_rain", category: "Water", emoji: "🌧️"),
        Sound(id: "thunderstorm", name: "Thunderstorm", fileName: "water_thunderstorm", category: "Water", emoji: "⛈️"),
        Sound(id: "ocean_waves", name: "Ocean Waves", fileName: "water_ocean_waves", category: "Water", emoji: "🌊"),
        Sound(id: "stream", name: "Gentle Stream", fileName: "water_stream", category: "Water", emoji: "💧"),
        Sound(id: "waterfall", name: "Waterfall", fileName: "water_waterfall", category: "Water", emoji: "🏞️"),
        
        // Nature
        Sound(id: "forest_birds", name: "Forest Birds", fileName: "nature_forest_birds", category: "Nature", emoji: "🐦"),
        Sound(id: "crickets", name: "Summer Crickets", fileName: "nature_crickets", category: "Nature", emoji: "🦗"),
        Sound(id: "wind", name: "Wind", fileName: "nature_wind", category: "Nature", emoji: "💨"),
        Sound(id: "distant_thunder", name: "Distant Thunder", fileName: "nature_distant_thunder", category: "Nature", emoji: "🌩️"),
        
        // Indoor
        Sound(id: "fireplace", name: "Fireplace", fileName: "indoor_fireplace", category: "Indoor", emoji: "🔥"),
        Sound(id: "fan", name: "Electric Fan", fileName: "indoor_fan", category: "Indoor", emoji: "🌀"),
        Sound(id: "cafe", name: "Café Ambience", fileName: "indoor_cafe", category: "Indoor", emoji: "☕"),
        Sound(id: "train", name: "Train Journey", fileName: "indoor_train", category: "Indoor", emoji: "🚂"),
        
        // Baby
        Sound(id: "womb_heartbeat", name: "Womb Heartbeat", fileName: "baby_womb_heartbeat", category: "Baby", emoji: "💓"),
        Sound(id: "womb_blood_flow", name: "Womb Blood Flow", fileName: "baby_womb_blood_flow", category: "Baby", emoji: "🫀"),
        Sound(id: "shushing", name: "Gentle Shushing", fileName: "baby_shushing", category: "Baby", emoji: "🤫"),
        Sound(id: "pink_noise", name: "Pink Noise", fileName: "baby_pink_noise", category: "Baby", emoji: "〰️"),
        Sound(id: "cat_purring", name: "Cat Purring", fileName: "baby_cat_purring", category: "Baby", emoji: "🐱"),
    ]
    
    static func sounds(for category: SoundCategory) -> [Sound] {
        allSounds.filter { $0.category == category.rawValue }
    }
}
