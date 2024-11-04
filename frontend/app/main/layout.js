"use client";
import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function MainLayout({ children }) {
  const router = useRouter();

  useEffect(() => {
    const username = sessionStorage.getItem('username');
    if (!username) {
      router.push('/'); // Redirect to login if not logged in
    }
  }, [router]);

  return <>{children}</>;
}