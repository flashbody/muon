import SwiftUI

struct PaywallView: View {
    @EnvironmentObject var storeManager: StoreManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                VStack(spacing: 24) {
                    Spacer()
                    
                    // Icon
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 64))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.cyan, .blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    // Title
                    Text("Unlock Full Mix")
                        .font(.system(size: 26, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    
                    // Features
                    VStack(alignment: .leading, spacing: 14) {
                        FeatureRow(icon: "slider.horizontal.3", text: "Mix up to 4 sounds together")
                        FeatureRow(icon: "moon.zzz.fill", text: "Sleep timer with gentle fade-out")
                        FeatureRow(icon: "heart.fill", text: "Save your favorite mixes")
                        FeatureRow(icon: "infinity", text: "One-time purchase, yours forever")
                    }
                    .padding(.vertical, 8)
                    
                    Spacer()
                    
                    // Price & Purchase
                    VStack(spacing: 12) {
                        if let product = storeManager.product {
                            Text(product.displayPrice)
                                .font(.system(size: 36, weight: .bold))
                                .foregroundColor(.white)
                            
                            Text("One-time purchase · No subscription")
                                .font(.system(size: 13))
                                .foregroundColor(.gray)
                            
                            Button(action: {
                                Task { await storeManager.purchase() }
                            }) {
                                Text("Unlock Muon Premium")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.black)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 52)
                                    .background(Color.cyan)
                                    .cornerRadius(14)
                            }
                            .disabled(storeManager.isLoading)
                        } else if storeManager.isLoading {
                            ProgressView()
                                .tint(.cyan)
                        } else {
                            Text("Unable to load price")
                                .foregroundColor(.gray)
                            
                            Button("Retry") {
                                Task { await storeManager.loadProduct() }
                            }
                            .foregroundColor(.cyan)
                        }
                        
                        Button("Restore Purchase") {
                            Task { await storeManager.restore() }
                        }
                        .font(.system(size: 13))
                        .foregroundColor(.gray)
                        
                        if let error = storeManager.errorMessage {
                            Text(error)
                                .font(.system(size: 12))
                                .foregroundColor(.red.opacity(0.8))
                        }
                    }
                    .padding(.bottom, 20)
                }
                .padding(.horizontal, 24)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.gray)
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
        .onChange(of: storeManager.isPurchased) { purchased in
            if purchased { dismiss() }
        }
    }
}

struct FeatureRow: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(.cyan)
                .frame(width: 24)
            
            Text(text)
                .font(.system(size: 15))
                .foregroundColor(.white.opacity(0.85))
        }
    }
}
