// src/app/types/next-auth.d.ts

import NextAuth, { DefaultSession, DefaultUser } from "next-auth";

// This is where we extend the Session and JWT types from next-auth.
// It ensures that TypeScript knows about the 'id' property we're adding.

// Augment the next-auth module
declare module "next-auth" {
  /**
   * The extended session object.
   */
  interface Session {
    user: {
      /** The user's unique ID. */
      id: string;
    } & DefaultSession["user"];
  }

  /**
   * The extended JWT token.
   */
  interface JWT {
    id: string;
  }

  /**
   * The extended user object.
   */
  interface User {
    id: string;
  }
}
