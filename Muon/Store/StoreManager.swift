import Foundation
import StoreKit

/// StoreKit 2 管理器 - 一次性买断制
@MainActor
final class StoreManager: ObservableObject {
    
    @Published var isPurchased: Bool = false
    @Published var product: Product?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    static let productId = "com.weaveon.muon.premium"
    
    private var transactionListener: Task<Void, Error>?
    
    init() {
        transactionListener = listenForTransactions()
        
        Task {
            await checkPurchaseStatus()
            await loadProduct()
        }
    }
    
    deinit {
        transactionListener?.cancel()
    }
    
    // MARK: - Load Product
    
    func loadProduct() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let products = try await Product.products(for: [Self.productId])
            product = products.first
            
            if product == nil {
                errorMessage = "Product not available"
            }
        } catch {
            errorMessage = "Failed to load product"
            print("Product load error: \(error)")
        }
        
        isLoading = false
    }
    
    // MARK: - Purchase
    
    func purchase() async {
        guard let product = product else { return }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let result = try await product.purchase()
            
            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                isPurchased = true
                await transaction.finish()
                
            case .userCancelled:
                break
                
            case .pending:
                errorMessage = "Purchase pending"
                
            @unknown default:
                break
            }
        } catch {
            errorMessage = "Purchase failed"
            print("Purchase error: \(error)")
        }
        
        isLoading = false
    }
    
    // MARK: - Restore
    
    func restore() async {
        isLoading = true
        
        do {
            try await AppStore.sync()
            await checkPurchaseStatus()
        } catch {
            errorMessage = "Restore failed"
        }
        
        isLoading = false
    }
    
    // MARK: - Check Status
    
    func checkPurchaseStatus() async {
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result {
                if transaction.productID == Self.productId {
                    isPurchased = true
                    return
                }
            }
        }
    }
    
    // MARK: - Transaction Listener
    
    private func listenForTransactions() -> Task<Void, Error> {
        let productId = Self.productId
        return Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    if transaction.productID == productId {
                        await MainActor.run { [weak self] in
                            self?.isPurchased = true
                        }
                    }
                    await transaction.finish()
                }
            }
        }
    }
    
    // MARK: - Verification
    
    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.verificationFailed
        case .verified(let safe):
            return safe
        }
    }
}

enum StoreError: Error {
    case verificationFailed
}
