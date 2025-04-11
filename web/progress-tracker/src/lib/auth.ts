import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { getDb } from '@/lib/db';
import bcrypt from 'bcryptjs';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "用户名", type: "text" },
        password: { label: "密码", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          const db = await getDb();
          const user = await db.get('SELECT * FROM Users WHERE username = ?', [credentials.username]);
          
          if (!user) {
            return null;
          }
          
          const isPasswordValid = await bcrypt.compare(credentials.password, user.password_hash);
          
          if (!isPasswordValid) {
            return null;
          }
          
          return {
            id: user.id,
            name: user.name,
            username: user.username,
            role: user.role,
            email: user.email || '',
          };
        } catch (error) {
          console.error('认证错误:', error);
          return null;
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30天
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = user.role;
        token.username = user.username;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
        session.user.username = token.username as string;
      }
      return session;
    }
  },
  pages: {
    signIn: '/login',
    error: '/login',
  },
  secret: process.env.NEXTAUTH_SECRET || 'your-secret-key',
};

// 类型扩展
declare module 'next-auth' {
  interface User {
    id: string;
    username: string;
    role: string;
  }
  
  interface Session {
    user: {
      id: string;
      name: string;
      username: string;
      role: string;
      email?: string;
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string;
    username: string;
    role: string;
  }
}
