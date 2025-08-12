import { api } from './api';
import type { Chapter } from '@/types';

export const chapterService = {
  // Get all chapters for a project
  async getChapters(projectId: number): Promise<Chapter[]> {
    const response = await api.get(`/projects/${projectId}/chapters`);
    return response.data;
  },

  // Get a single chapter
  async getChapter(projectId: number, chapterId: number): Promise<Chapter> {
    const response = await api.get(`/projects/${projectId}/chapters/${chapterId}`);
    return response.data;
  },

  // Create a new chapter
  async createChapter(
    projectId: number,
    data: { title: string; content?: string; position?: number }
  ): Promise<Chapter> {
    const response = await api.post(`/projects/${projectId}/chapters`, data);
    return response.data;
  },

  // Update a chapter
  async updateChapter(
    projectId: number,
    chapterId: number,
    data: { title?: string; content?: string; position?: number }
  ): Promise<Chapter> {
    const response = await api.patch(
      `/projects/${projectId}/chapters/${chapterId}`,
      data
    );
    return response.data;
  },

  // Delete a chapter
  async deleteChapter(projectId: number, chapterId: number): Promise<void> {
    await api.delete(`/projects/${projectId}/chapters/${chapterId}`);
  },

  // Reorder chapters
  async reorderChapters(
    projectId: number,
    chapters: { chapter_id: number; new_position: number }[]
  ): Promise<Chapter[]> {
    const response = await api.post(
      `/projects/${projectId}/chapters/reorder`,
      { chapters }
    );
    return response.data;
  },

  // Import chapter from markdown
  async importChapter(projectId: number, markdown: string): Promise<Chapter> {
    const response = await api.post(
      `/projects/${projectId}/chapters/import`,
      markdown,
      {
        headers: {
          'Content-Type': 'text/markdown',
        },
      }
    );
    return response.data;
  },

  // Export chapter as markdown
  async exportChapter(
    projectId: number,
    chapterId: number,
    includeMetadata = false
  ): Promise<string> {
    const response = await api.get(
      `/projects/${projectId}/chapters/${chapterId}/export`,
      {
        params: { include_metadata: includeMetadata },
        headers: {
          Accept: 'text/markdown',
        },
      }
    );
    return response.data;
  },

  // Export all chapters as markdown
  async exportAllChapters(
    projectId: number,
    includeMetadata = false
  ): Promise<string> {
    const response = await api.get(
      `/projects/${projectId}/chapters/export`,
      {
        params: { include_metadata: includeMetadata },
        headers: {
          Accept: 'text/markdown',
        },
      }
    );
    return response.data;
  },
};