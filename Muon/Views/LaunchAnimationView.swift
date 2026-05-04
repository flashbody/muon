import SwiftUI

/// 启动动画页 - 2.5秒品牌展示动画
struct LaunchAnimationView: View {
    @State private var showIcon = false
    @State private var showTitle = false
    @State private var showSubtitle = false
    @State private var pulseScale: CGFloat = 1.0
    @State private var waveOffset: CGFloat = 0
    @State private var opacity: Double = 1.0
    
    let onComplete: () -> Void
    
    var body: some View {
        ZStack {
            // Background
            Color.black.ignoresSafeArea()
            
            // Subtle wave animation in background
            WaveShape(offset: waveOffset)
                .fill(
                    LinearGradient(
                        colors: [Color.cyan.opacity(0.05), Color.blue.opacity(0.03)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(height: 300)
                .offset(y: 100)
                .ignoresSafeArea()
            
            VStack(spacing: 20) {
                Spacer()
                
                // App Icon - breathing pulse animation
                ZStack {
                    // Outer glow ring
                    Circle()
                        .stroke(
                            LinearGradient(
                                colors: [.cyan.opacity(0.3), .blue.opacity(0.1)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 2
                        )
                        .frame(width: 100, height: 100)
                        .scaleEffect(pulseScale)
                        .opacity(showIcon ? 0.6 : 0)
                    
                    // Inner icon
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 72))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.cyan, .blue.opacity(0.8)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .scaleEffect(showIcon ? 1.0 : 0.3)
                        .opacity(showIcon ? 1.0 : 0)
                }
                
                // App Name
                Text("Muon")
                    .font(.system(size: 38, weight: .ultraLight, design: .rounded))
                    .foregroundColor(.white)
                    .opacity(showTitle ? 1.0 : 0)
                    .offset(y: showTitle ? 0 : 15)
                
                // Tagline
                Text("Sleep · Focus · Soothe")
                    .font(.system(size: 14, weight: .regular, design: .rounded))
                    .foregroundColor(.gray)
                    .tracking(3)
                    .opacity(showSubtitle ? 1.0 : 0)
                    .offset(y: showSubtitle ? 0 : 10)
                
                Spacer()
                Spacer()
            }
        }
        .opacity(opacity)
        .onAppear {
            startAnimation()
        }
    }
    
    private func startAnimation() {
        // Step 1: Icon appears (0.0s - 0.5s)
        withAnimation(.spring(response: 0.6, dampingFraction: 0.7)) {
            showIcon = true
        }
        
        // Step 2: Pulse breathing starts
        withAnimation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true)) {
            pulseScale = 1.15
        }
        
        // Step 3: Wave animation
        withAnimation(.linear(duration: 3.0).repeatForever(autoreverses: false)) {
            waveOffset = .pi * 2
        }
        
        // Step 4: Title appears (0.4s)
        withAnimation(.easeOut(duration: 0.5).delay(0.4)) {
            showTitle = true
        }
        
        // Step 5: Subtitle appears (0.7s)
        withAnimation(.easeOut(duration: 0.5).delay(0.7)) {
            showSubtitle = true
        }
        
        // Step 6: Fade out and complete (2.5s)
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.2) {
            withAnimation(.easeIn(duration: 0.3)) {
                opacity = 0
            }
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
            onComplete()
        }
    }
}

/// 波浪形状
struct WaveShape: Shape {
    var offset: CGFloat
    
    var animatableData: CGFloat {
        get { offset }
        set { offset = newValue }
    }
    
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let width = rect.width
        let height = rect.height
        let midHeight = height / 2
        
        path.move(to: CGPoint(x: 0, y: midHeight))
        
        for x in stride(from: 0, through: width, by: 2) {
            let relativeX = x / width
            let y = midHeight + sin((relativeX * .pi * 2) + offset) * 20
            path.addLine(to: CGPoint(x: x, y: y))
        }
        
        path.addLine(to: CGPoint(x: width, y: height))
        path.addLine(to: CGPoint(x: 0, y: height))
        path.closeSubpath()
        
        return path
    }
}

#Preview {
    LaunchAnimationView(onComplete: {})
}
