// hooks/useAuth.js — Firebase auth state
import { useState, useEffect } from 'react';
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
} from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db, googleProvider } from '../firebase';

export function useAuth() {
  const [user, setUser]       = useState(undefined); // undefined = loading
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return unsub;
  }, []);

  const _ensureUserDoc = async (u) => {
    const ref = doc(db, 'users', u.uid);
    await setDoc(ref, {
      displayName: u.displayName || '',
      email: u.email || '',
      createdAt: serverTimestamp(),
    }, { merge: true });
  };

  const loginEmail = async (email, password) => {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    await _ensureUserDoc(cred.user);
    return cred.user;
  };

  const registerEmail = async (email, password, displayName) => {
    const cred = await createUserWithEmailAndPassword(auth, email, password);
    if (displayName) await updateProfile(cred.user, { displayName });
    await _ensureUserDoc({ ...cred.user, displayName });
    return cred.user;
  };

  const loginGoogle = async () => {
    const cred = await signInWithPopup(auth, googleProvider);
    await _ensureUserDoc(cred.user);
    return cred.user;
  };

  const logout = () => signOut(auth);

  return { user, loading, loginEmail, registerEmail, loginGoogle, logout };
}
