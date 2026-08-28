// hooks/useChats.js — Firestore chat CRUD + soft-delete
import { useState, useEffect, useCallback } from 'react';
import {
  collection, doc, addDoc, updateDoc, getDoc, setDoc,
  query, orderBy, where, serverTimestamp, onSnapshot,
  increment,
} from 'firebase/firestore';
import { db } from '../firebase';

const MAX_CHATS_PER_DAY = 20;

export function useChats(user) {
  const [chats,   setChats]   = useState([]);
  const [loading, setLoading] = useState(true);

  // Real-time listener for non-deleted chats, ordered by updatedAt desc
  useEffect(() => {
    if (!user) { setChats([]); setLoading(false); return; }

    const q = query(
      collection(db, 'users', user.uid, 'chats'),
      where('deletedAt', '==', null),
      orderBy('updatedAt', 'desc'),
    );
    const unsub = onSnapshot(q, (snap) => {
      setChats(snap.docs.map((d) => ({ id: d.id, ...d.data() })));
      setLoading(false);
    });
    return unsub;
  }, [user?.uid]);

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  const _getDailyCount = async (uid) => {
    const today = new Date().toISOString().slice(0, 10);
    const ref   = doc(db, 'users', uid, 'rateLimits', today);
    const snap  = await getDoc(ref);
    return snap.exists() ? (snap.data().chatsCreated || 0) : 0;
  };

  const _incrementDailyCount = async (uid) => {
    const today    = new Date().toISOString().slice(0, 10);
    const limitRef = doc(db, 'users', uid, 'rateLimits', today);
    await setDoc(limitRef, { chatsCreated: increment(1) }, { merge: true });
  };

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  const createChat = useCallback(async (firstMessage = 'New Chat') => {
    if (!user) throw new Error('Not authenticated');

    // Client-side pre-check (server enforces too)
    const count = await _getDailyCount(user.uid);
    if (count >= MAX_CHATS_PER_DAY) {
      throw new Error(
        `You've created ${MAX_CHATS_PER_DAY} chats today — the daily limit. This resets at midnight.`
      );
    }

    const title = (firstMessage || '').slice(0, 60) || 'New Chat';
    const now   = serverTimestamp();

    const ref = await addDoc(collection(db, 'users', user.uid, 'chats'), {
      title,
      createdAt:    now,
      updatedAt:    now,
      apiCallCount: 0,
      deletedAt:    null,
    });

    await _incrementDailyCount(user.uid);
    return ref.id;
  }, [user?.uid]);

  const renameChat = useCallback(async (chatId, newTitle) => {
    if (!user) return;
    await updateDoc(doc(db, 'users', user.uid, 'chats', chatId), {
      title:     newTitle,
      updatedAt: serverTimestamp(),
    });
  }, [user?.uid]);

  const deleteChat = useCallback(async (chatId) => {
    if (!user) return;
    // Soft-delete: mark deletedAt, never hard-delete
    await updateDoc(doc(db, 'users', user.uid, 'chats', chatId), {
      deletedAt: serverTimestamp(),
    });
  }, [user?.uid]);

  return { chats, loading, createChat, renameChat, deleteChat };
}
