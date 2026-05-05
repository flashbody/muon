import SwiftUI

/// 启动动画页 - 2.5秒品牌展示动画（欧美简约风格）
struct LaunchAnimationView: View {
    @State private var showIcon = false
    @State private var showTitle = false
    @State private var showTagline = false
    @State private var pulseScale: CGFloat = 1.0
    @State private var opacity: Double = 1.0
    
    let onComplete: () -> Void
    
    var body: some View {
        ZStack {
            // 背景 - 纯黑（欧美App常用）
            Color.black
                .ignoresSafeArea()
            
            // 背景微光效果（极其微妙）
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            Color.cyan.opacity(0.08),
                            Color.clear
                        ],
                        center: .center,
                        startRadius: 50,
                        endRadius: 300
                    )
                )
                .frame(width: 600, height: 600)
                .blur(radius: 60)
                .offset(y: -50)
            
            // 主内容 - 垂直居中
            VStack(spacing: 28) {
                Spacer()
                
                // 图标区域 - 呼吸脉动效果
                ZStack {
                    // 外圈脉动
                    Circle()
                        .stroke(Color.cyan.opacity(0.2), lineWidth: 1.5)
                        .frame(width: 110, height: 110)
                        .scaleEffect(pulseScale)
                        .opacity(showIcon ? 0.8 : 0)
                    
                    // 图标
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 68, weight: .ultraLight))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [Color.cyan, Color.blue.opacity(0.7)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .scaleEffect(showIcon ? 1.0 : 0.5)
                        .opacity(showIcon ? 1.0 : 0)
                }
                
                // 品牌名 - 超大超轻字体（欧美高端App风格）
                Text("Muon")
                    .font(.system(size: 42, weight: .ultraLight, design: .rounded))
                    .foregroundColor(.white)
                    .tracking(2)
                    .opacity(showTitle ? 1.0 : 0)
                    .offset(y: showTitle ? 0 : 20)
                
                // 标语 - 极简
                Text("Ambient Soundscape")
                    .font(.system(size: 13, weight: .regular, design: .rounded))
                    .foregroundColor(Color.white.opacity(0.4))
                    .tracking(4)
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
        // 1. 图标出现（0.0s）
        withAnimation(.spring(response: 0.7, dampingFraction: 0.65)) {
            showIcon = true
        }
        
        // 2. 呼吸脉动（循环）
        withAnimation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true)) {
            pulseScale = 1.2
        }
        
        // 3. 标题出现（0.3s）
        withAnimation(.easeOut(duration: 0.6).delay(0.3)) {
            showTitle = true
        }
        
        // 4. 标语出现（0.6s）
        withAnimation(.easeOut(duration: 0.6).delay(0.6)) {
            showTagline = true
        }
        
        // 5. 淡出（2.0s）
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            withAnimation(.easeIn(duration: 0.5)) {
                opacity = 0
            }
        }
        
        // 6. 完成
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
            onComplete()
        }
    }
}

#Preview {
    LaunchAnimationView(onComplete: {})
}
