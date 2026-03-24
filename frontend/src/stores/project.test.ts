/** @vitest-environment jsdom */
import { test, expect, beforeEach } from 'vitest';
import { useProjectStore, type Project } from './project';

beforeEach(() => {
  // 重置 store 状态
  useProjectStore.setState({
    projects: [],
    currentProject: null,
    loading: false,
    error: null,
  });
});

test('Project Store - 初始状态', () => {
  const state = useProjectStore.getState();
  expect(state.projects).toEqual([]);
  expect(state.currentProject).toBeNull();
  expect(state.loading).toBe(false);
  expect(state.error).toBeNull();
});

test('Project Store - setProjects', () => {
  const mockProjects: Project[] = [
    { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
    { id: '2', name: '项目 2', description: '描述 2', progress: 80, phase: 'executing', status: 'active' },
  ];

  useProjectStore.getState().setProjects(mockProjects);

  const state = useProjectStore.getState();
  expect(state.projects).toEqual(mockProjects);
  expect(state.error).toBeNull();
});

test('Project Store - addProject', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
  ]);

  const newProject: Project = {
    id: '2',
    name: '新项目',
    description: '新描述',
    progress: 0,
    phase: 'planning',
    status: 'active',
  };

  useProjectStore.getState().addProject(newProject);

  const state = useProjectStore.getState();
  expect(state.projects).toHaveLength(2);
  expect(state.projects[1]).toEqual(newProject);
});

test('Project Store - updateProject', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '原描述', progress: 50, phase: 'planning', status: 'active' },
  ]);

  useProjectStore.getState().updateProject('1', { name: '更新后的项目', progress: 75 });

  const state = useProjectStore.getState();
  expect(state.projects[0].name).toBe('更新后的项目');
  expect(state.projects[0].progress).toBe(75);
});

test('Project Store - updateProject 同时更新 currentProject', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述', progress: 50, phase: 'planning', status: 'active' },
  ]);
  useProjectStore.getState().setCurrentProject({
    id: '1',
    name: '项目 1',
    description: '描述',
    progress: 50,
    phase: 'planning',
    status: 'active',
  });

  useProjectStore.getState().updateProject('1', { name: '更新后的项目' });

  const state = useProjectStore.getState();
  expect(state.currentProject?.name).toBe('更新后的项目');
});

test('Project Store - deleteProject', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
    { id: '2', name: '项目 2', description: '描述 2', progress: 80, phase: 'executing', status: 'active' },
  ]);

  useProjectStore.getState().deleteProject('1');

  const state = useProjectStore.getState();
  expect(state.projects).toHaveLength(1);
  expect(state.projects[0].id).toBe('2');
});

test('Project Store - deleteProject 同时更新 currentProject', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述', progress: 50, phase: 'planning', status: 'active' },
  ]);
  useProjectStore.getState().setCurrentProject({
    id: '1',
    name: '项目 1',
    description: '描述',
    progress: 50,
    phase: 'planning',
    status: 'active',
  });

  useProjectStore.getState().deleteProject('1');

  const state = useProjectStore.getState();
  expect(state.currentProject).toBeNull();
});

test('Project Store - updateProjectProgress', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述', progress: 50, phase: 'planning', status: 'active' },
  ]);

  useProjectStore.getState().updateProjectProgress('1', 80);

  const state = useProjectStore.getState();
  expect(state.projects[0].progress).toBe(80);
});

test('Project Store - updateProjectPhase', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述', progress: 50, phase: 'planning', status: 'active' },
  ]);

  useProjectStore.getState().updateProjectPhase('1', 'executing');

  const state = useProjectStore.getState();
  expect(state.projects[0].phase).toBe('executing');
});

test('Project Store - setLoading', () => {
  useProjectStore.getState().setLoading(true);
  expect(useProjectStore.getState().loading).toBe(true);

  useProjectStore.getState().setLoading(false);
  expect(useProjectStore.getState().loading).toBe(false);
});

test('Project Store - setError', () => {
  useProjectStore.getState().setError('错误信息');
  expect(useProjectStore.getState().error).toBe('错误信息');

  useProjectStore.getState().setError(null);
  expect(useProjectStore.getState().error).toBeNull();
});

test('Project Store - setCurrentProject', () => {
  const project: Project = {
    id: '1',
    name: '当前项目',
    description: '描述',
    progress: 50,
    phase: 'planning',
    status: 'active',
  };

  useProjectStore.getState().setCurrentProject(project);
  expect(useProjectStore.getState().currentProject).toEqual(project);
});

test('Project Store - deleteProject 不影响其他项目', () => {
  useProjectStore.getState().setProjects([
    { id: '1', name: '项目 1', description: '描述 1', progress: 50, phase: 'planning', status: 'active' },
    { id: '2', name: '项目 2', description: '描述 2', progress: 80, phase: 'executing', status: 'active' },
    { id: '3', name: '项目 3', description: '描述 3', progress: 30, phase: 'reviewing', status: 'active' },
  ]);
  useProjectStore.getState().setCurrentProject({
    id: '2',
    name: '项目 2',
    description: '描述 2',
    progress: 80,
    phase: 'executing',
    status: 'active',
  });

  useProjectStore.getState().deleteProject('1');

  const state = useProjectStore.getState();
  expect(state.projects).toHaveLength(2);
  expect(state.currentProject?.id).toBe('2');
});
