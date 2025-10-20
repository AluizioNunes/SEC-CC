import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type PermissionMatrix = {
  screens: {
    usuarios?: { view: boolean; create: boolean; edit: boolean; delete: boolean };
    perfil?: { view: boolean; create: boolean; edit: boolean; delete: boolean };
    permissoes?: { view: boolean; create: boolean; edit: boolean; delete: boolean };
  };
};

export type Profile = {
  id: string;
  name: string;
  description?: string;
  permissions?: PermissionMatrix;
};

export type AdminUser = {
  id: string;
  name: string;
  email: string;
  type: 'PF' | 'PJ';
  status: 'approved' | 'pending' | 'active' | 'inactive';
  profileId: string;
  createdBy?: { id: string; name: string };
  createdAt?: number;
};

export type AdminLog = {
  id: string;
  entity: 'user' | 'profile' | 'permission';
  entityId: string;
  action: 'create' | 'update' | 'delete';
  at: number;
  by: { id: string; name: string };
  details?: Record<string, any>;
};

const STORAGE_KEY = 'sec-admin-store';

export type AdminStore = {
  users: AdminUser[];
  profiles: Profile[];
  permissions: Record<string, PermissionMatrix>;
  logs?: AdminLog[];
};

const AdminContext = createContext<any>(null);

export const AdminProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [store, setStore] = useState<AdminStore>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try { return JSON.parse(raw); } catch {}
    }
    return {
      users: [],
      profiles: [
        { id: 'p-admin', name: 'Administrador', description: 'Acesso total', permissions: { screens: { usuarios: { view: true, create: true, edit: true, delete: true }, perfil: { view: true, create: true, edit: true, delete: true }, permissoes: { view: true, create: true, edit: true, delete: true } } } },
        { id: 'p-usuario', name: 'Usuário', description: 'Acesso limitado', permissions: { screens: { usuarios: { view: true, create: false, edit: false, delete: false }, perfil: { view: false, create: false, edit: false, delete: false }, permissoes: { view: false, create: false, edit: false, delete: false } } } },
      ],
      permissions: {},
      logs: [],
    };
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  }, [store]);

  const addLog = (log: Omit<AdminLog, 'id' | 'at'> & { id?: string; at?: number }) => {
    setStore(prev => ({ ...prev, logs: [...(prev.logs || []), { id: log.id || crypto.randomUUID(), at: log.at || Date.now(), entity: log.entity, entityId: log.entityId, action: log.action, by: log.by, details: log.details }] }));
  };

  // Users
  const addUser = (u: Omit<AdminUser, 'id'>, actor?: { id: string; name: string }) => {
    const id = crypto.randomUUID();
    setStore(prev => ({ ...prev, users: [...prev.users, { ...u, id }] }));
    if (actor) addLog({ entity: 'user', entityId: id, action: 'create', by: actor, details: u });
  };
  const updateUser = (id: string, patch: Partial<AdminUser>, actor?: { id: string; name: string }) => {
    setStore(prev => ({ ...prev, users: prev.users.map(x => x.id === id ? { ...x, ...patch } : x) }));
    if (actor) addLog({ entity: 'user', entityId: id, action: 'update', by: actor, details: patch });
  };
  const deleteUser = (id: string, actor?: { id: string; name: string }) => {
    setStore(prev => ({ ...prev, users: prev.users.filter(x => x.id !== id) }));
    if (actor) addLog({ entity: 'user', entityId: id, action: 'delete', by: actor });
  };

  // Profiles
  const addProfile = (p: Omit<Profile, 'id'>, actor?: { id: string; name: string }) => {
    const id = crypto.randomUUID();
    setStore(prev => ({ ...prev, profiles: [...prev.profiles, { ...p, id }] }));
    if (actor) addLog({ entity: 'profile', entityId: id, action: 'create', by: actor, details: p });
  };
  const updateProfile = (id: string, patch: Partial<Profile>, actor?: { id: string; name: string }) => {
    setStore(prev => ({ ...prev, profiles: prev.profiles.map(x => x.id === id ? { ...x, ...patch } : x) }));
    if (actor) addLog({ entity: 'profile', entityId: id, action: 'update', by: actor, details: patch });
  };
  const deleteProfile = (id: string, actor?: { id: string; name: string }) => {
    setStore(prev => ({ ...prev, profiles: prev.profiles.filter(x => x.id !== id) }));
    if (actor) addLog({ entity: 'profile', entityId: id, action: 'delete', by: actor });
  };

  // Permissions
  const getPermissionsForProfile = (profileId: string): PermissionMatrix | undefined => {
    const profilePerms = store.profiles.find(p => p.id === profileId)?.permissions;
    return profilePerms || store.permissions[profileId];
  };
  const setPermissionsForProfile = (profileId: string, pm: PermissionMatrix, actor?: { id: string; name: string }) => {
    setStore(prev => ({ ...prev, permissions: { ...prev.permissions, [profileId]: pm } }));
    if (actor) addLog({ entity: 'permission', entityId: profileId, action: 'update', by: actor, details: pm });
  };

  const value = useMemo(() => ({
    users: store.users,
    profiles: store.profiles,
    permissions: store.permissions,
    logs: store.logs || [],
    addUser, updateUser, deleteUser,
    addProfile, updateProfile, deleteProfile,
    getPermissionsForProfile, setPermissionsForProfile,
    addLog,
  }), [store]);

  return <AdminContext.Provider value={value}>{children}</AdminContext.Provider>;
};

export const useAdmin = () => useContext(AdminContext);