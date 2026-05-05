import SwiftUI

/// 启动动画页 - 世界五百强风格品牌展示
/// 从UILaunchScreen静态启动图平滑过渡到动画，再过渡到主界面
struct LaunchAnimationView: View {
    @State private var showIcon = false
    @State private var showTitle = false
    @State private var showTagline = false
    @State private var pulseScale: CGFloat = 1.0
    @State private var glowOpacity: Double = 0
    @State private var opacity: Double = 1.0
    
    let onComplete: () -> Void
    
    var body: some View {
        ZStack {
            // 纯黑背景（与UILaunchScreen一致）
            Color.black
                .ignoresSafeArea()
            
            // 中心微光（声波脉冲感）
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            Color.cyan.opacity(0.12),
                            Color.cyan.opacity(0.04),
                            Color.clear
                        ],
                        center: .center,
                        startRadius: 30,
                        endRadius: 200
                    )
                )
                .frame(width: 500, height: 500)
                .scaleEffect(pulseScale)
                .opacity(glowOpacity)
            
            // 主内容 - 垂直居中
            VStack(spacing: 24) {
                Spacer()
                
                // 图标 - 与启动图一致的声波图标
                ZStack {
                    // 外圈脉动光环
                    Circle()
                        .stroke(Color.cyan.opacity(0.15), lineWidth: 1)
                        .frame(width: 120, height: 120)
                        .scaleEffect(pulseScale)
                        .opacity(showIcon ? 0.8 : 0)
                    
                    // 第二圈脉动
                    Circle()
                        .stroke(Color.cyan.opacity(0.08), lineWidth: 0.5)
                        .frame(width: 150, height: 150)
                        .scaleEffect(pulseScale * 1.1)
                        .opacity(showIcon ? 0.5 : 0)
                    
                    // 品牌图标
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 72, weight: .ultraLight))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [
                                    Color(red: 0, green: 0.82, blue: 0.91),
                                    Color(red: 0, green: 0.55, blue: 0.75)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .scaleEffect(showIcon ? 1.0 : 0.6)
                        .opacity(showIcon ? 1.0 : 0)
                }
                
                // 品牌名 - 极简超轻
                Text("Muon")
                    .font(.system(size: 44, weight: .ultraLight, design: .rounded))
                    .foregroundColor(.white)
                    .tracking(3)
                    .opacity(showTitle ? 1.0 : 0)
                    .offset(y: showTitle ? 0 : 20)
                
                // 标语 - 极淡
                Text("Ambient Soundscape")
                    .font(.system(size: 12, weight: .regular, design: .rounded))
                    .foregroundColor(Color.white.opacity(0.35))
                    .tracking(5)
                    .opacity(showTagline ? 1.0 : 0)
                    .offset(y: showTagline ? 0 : 10)
                
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
        // 1. 图标从中心展开（0.0s）
        withAnimation(.spring(response: 0.8, dampingFraction: 0.6)) {
            showIcon = true
        }
        
        // 2. 微光脉动（0.3s）
        withAnimation(.easeOut(duration: 0.6).delay(0.3)) {
            glowOpacity = 1.0
        }
        
        // 3. 呼吸脉动（循环）
        withAnimation(.easeInOut(duration: 1.8).repeatForever(autoreverses: true).delay(0.5)) {
            pulseScale = 1.15
        }
        
        // 4. 品牌名出现（0.4s）
        withAnimation(.easeOut(duration: 0.7).delay(0.4)) {
            showTitle = true
        }
        
        // 5. 标语出现（0.7s）
        withAnimation(.easeOut(duration: 0.6).delay(0.7)) {
            showTagline = true
        }
        
        // 6. 淡出（2.0s）
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            withAnimation(.easeIn(duration: 0.5)) {
                opacity = 0
            }
        }
        
        // 7. 完成
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
            onComplete()
        }
    }
}

#Preview {
    LaunchAnimationView(onComplete: {})
}
