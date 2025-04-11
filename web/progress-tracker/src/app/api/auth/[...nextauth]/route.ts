// app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { getDb } from "@/lib/db";
import bcrypt from "bcryptjs";

export const authOptions = {
  // 使用 CredentialsProvider 进行用户名密码认证
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "用户名", type: "text", placeholder: "请输入用户名" },
        password: { label: "密码", type: "password", placeholder: "请输入密码" }
      },
      async authorize(credentials) {
        // 获取数据库连接
        const db = await getDb();
        if (!db) {
          throw new Error("数据库连接失败");
        }
        
        // 查询用户
        const user = await db.get('SELECT * FROM Users WHERE username = ?', [credentials?.username]);
        if (!user) {
          throw new Error("用户名或密码错误");
        }
        
        // 验证密码
        const isPasswordValid = await bcrypt.compare(credentials?.password || "", user.password_hash);
        if (!isPasswordValid) {
          throw new Error("用户名或密码错误");
        }
        
        // 返回用户对象
        return { 
          id: user.id, 
          username: user.username, 
          name: user.name, 
          role: user.role, 
          email: user.email 
        };
      }
    })
  ],
  // 使用 JWT 进行会话管理
  session: {
    strategy: "jwt" as const,
  },
  jwt: {
    secret: process.env.JWT_SECRET || "your-secret-key",
  },
  // 自定义页面（例如登录页）
  pages: {
    signIn: "/login",
  },
  secret: process.env.NEXTAUTH_SECRET || "your-nextauth-secret",
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };