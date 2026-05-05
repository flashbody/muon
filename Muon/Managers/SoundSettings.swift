import Foundation
import SwiftUI

class SoundSettings: ObservableObject {
    static let shared = SoundSettings()
    
    @AppStorage("useRealSound") var useRealSound: Bool = false {
        didSet {
            print("🔊 Sound mode changed: \(useRealSound ? "Real Recording" : "Algorithm")")
        }
    }
    
    private init() {}
}
