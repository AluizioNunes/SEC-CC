import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { UsersApi } from '../services/usersApi';
import type { UsuarioRecord } from '../services/usersApi';
import { PermissionsApi } from '../services/permissionsApi';
import { useAuth } from './AuthContext';

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
  const { user } = useAuth();
  const [store, setStore] = useState<AdminStore>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try { return JSON.parse(raw); } catch {}
    }
    return {
      users: [],
      profiles: [
        { id: 'p-master', name: 'Master', description: 'Acesso superior ao Admin', permissions: { screens: { usuarios: { view: true, create: true, edit: true, delete: true }, perfil: { view: true, create: true, edit: true, delete: true }, permissoes: { view: true, create: true, edit: true, delete: true } } } },
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

  // Mapeia UsuarioRecord (backend) -> AdminUser (frontend)
  const mapRecordToAdminUser = (rec: UsuarioRecord): AdminUser => {
    const up = (rec.Perfil || '').toUpperCase();
    const profileId = up === 'MASTER' ? 'p-master' : up === 'ADMINISTRADOR' ? 'p-admin' : 'p-usuario';
    return {
      id: String(rec.IdUsuario),
      name: rec.Nome ?? '',
      email: rec.Email ?? '',
      profileId,
      type: 'PF',
      status: 'active',
      createdBy: undefined,
      createdAt: undefined,
    };
  };

  // Carrega usuários reais do backend ao iniciar
  useEffect(() => {
    (async () => {
      try {
        const records = await UsersApi.list();
        setStore(prev => ({
          ...prev,
          users: records.map(mapRecordToAdminUser),
        }));
      } catch (err) {
        console.error('Erro ao listar usuários', err);
      }
    })();
  }, []);

  // Carrega permissões efetivas do backend para o usuário autenticado
  useEffect(() => {
    (async () => {
      try {
        if (!user || !user.id || user.id === 'guest') return;
        const token = typeof window !== 'undefined' ? localStorage.getItem('sec-token') : null;
        if (!token) return; // evita chamada sem token e consequente 401
        const resp = await PermissionsApi.getForUser(user.id);
        // Decide qual profileId interno usar (MASTER tem precedência funcional)
        const profileId = user.rawProfile === 'MASTER' ? 'p-master' : (user.profile === 'admin' ? 'p-admin' : 'p-usuario');
        const matrix = resp.matrix as PermissionMatrix; // compatível com nosso tipo
        setStore(prev => ({
          ...prev,
          permissions: { ...prev.permissions, [profileId]: matrix },
        }));
      } catch (err) {
        console.error('Erro ao carregar permissões do usuário', err);
      }
    })();
  }, [user?.id]);

  // Helper para obter nome de perfil pelo id
  const resolvePerfilNome = (profileId: string): string => {
    const profile = store.profiles.find(p => p.id === profileId);
    return profile ? profile.name : 'Usuário';
  };

  // Users
  const addUser = async (u: Omit<AdminUser, 'id'>, actor?: { id: string; name: string }) => {
    const payload = {
      Nome: u.name,
      Email: u.email,
      Perfil: resolvePerfilNome(u.profileId),
      Login: u.email || u.name,
      Cadastrante: actor?.name || 'Admin',
      TipoUpdate: 'CREATE',
    };
    try {
      const rec = await UsersApi.create(payload);
      const created = mapRecordToAdminUser(rec);
      setStore(prev => ({ ...prev, users: [created, ...prev.users] }));
      if (actor) addLog({ entity: 'user', entityId: created.id, action: 'create', by: actor, details: u });
    } catch (err) {
      console.error('Erro ao criar usuário', err);
      throw err;
    }
  };
  const updateUser = async (id: string, patch: Partial<AdminUser>, actor?: { id: string; name: string }) => {
    const numId = Number(id);
    const payload: any = {};
    if (patch.name !== undefined) payload.Nome = patch.name;
    if (patch.email !== undefined) payload.Email = patch.email;
    if (patch.profileId !== undefined) payload.Perfil = resolvePerfilNome(patch.profileId);
    payload.TipoUpdate = 'UPDATE';
    try {
      const rec = await UsersApi.update(numId, payload);
      const updated = mapRecordToAdminUser(rec);
      setStore(prev => ({ ...prev, users: prev.users.map(u => (u.id === id ? { ...u, ...updated } : u)) }));
      if (actor) addLog({ entity: 'user', entityId: id, action: 'update', by: actor, details: patch });
    } catch (err) {
      console.error('Erro ao atualizar usuário', err);
      throw err;
    }
  };
  const deleteUser = async (id: string, actor?: { id: string; name: string }) => {
    const numId = Number(id);
    try {
      await UsersApi.remove(numId);
      setStore(prev => ({ ...prev, users: prev.users.filter(u => u.id !== id) }));
      if (actor) addLog({ entity: 'user', entityId: id, action: 'delete', by: actor });
    } catch (err) {
      console.error('Erro ao remover usuário', err);
      throw err;
    }
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