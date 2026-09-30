import api from '@/utils/api'

// ====== Portal API ======
export const portalApi = {
  getHome: () => api.get('/v1/portal/home'),
  getCategories: (type?: string) => api.get('/v1/portal/categories', { params: { type } }),
  getArticles: (params: { page?: number; pageSize?: number; categoryId?: number }) =>
    api.get('/v1/portal/articles', { params }),
  getArticleDetail: (id: number) => api.get(`/v1/portal/articles/${id}`),
  getProducts: (params: { page?: number; pageSize?: number; categoryId?: number }) =>
    api.get('/v1/portal/products', { params }),
  getProductDetail: (id: number) => api.get(`/v1/portal/products/${id}`),
  getPage: (key: string) => api.get(`/v1/portal/pages/${key}`),
  submitMessage: (data: { name: string; phone: string; email?: string; content: string }) =>
    api.post('/v1/portal/messages', data),
}

// ====== Admin API ======
export const adminApi = {
  getDashboard: () => api.get('/v1/admin/dashboard'),
  getCategories: (type?: string) => api.get('/v1/admin/categories', { params: { type } }),
  createCategory: (data: any) => api.post('/v1/admin/categories', data),
  updateCategory: (id: number, data: any) => api.put(`/v1/admin/categories/${id}`, data),
  deleteCategory: (id: number) => api.delete(`/v1/admin/categories/${id}`),
  getArticles: (params: any) => api.get('/v1/admin/articles', { params }),
  createArticle: (data: any) => api.post('/v1/admin/articles', data),
  updateArticle: (id: number, data: any) => api.put(`/v1/admin/articles/${id}`, data),
  deleteArticle: (id: number) => api.delete(`/v1/admin/articles/${id}`),
  updateArticleStatus: (id: number, status: string) => api.put(`/v1/admin/articles/${id}/status`, { status }),
  getProducts: (params: any) => api.get('/v1/admin/products', { params }),
  createProduct: (data: any) => api.post('/v1/admin/products', data),
  updateProduct: (id: number, data: any) => api.put(`/v1/admin/products/${id}`, data),
  deleteProduct: (id: number) => api.delete(`/v1/admin/products/${id}`),
  getPages: () => api.get('/v1/admin/pages'),
  updatePage: (id: number, data: any) => api.put(`/v1/admin/pages/${id}`, data),
  getMessages: (params: any) => api.get('/v1/admin/messages', { params }),
  getMessage: (id: number) => api.get(`/v1/admin/messages/${id}`),
  markMessageRead: (id: number) => api.put(`/v1/admin/messages/${id}/read`),
  deleteMessage: (id: number) => api.delete(`/v1/admin/messages/${id}`),
  getBanners: () => api.get('/v1/admin/banners'),
  createBanner: (data: any) => api.post('/v1/admin/banners', data),
  updateBanner: (id: number, data: any) => api.put(`/v1/admin/banners/${id}`, data),
  deleteBanner: (id: number) => api.delete(`/v1/admin/banners/${id}`),
  getFriendLinks: () => api.get('/v1/admin/friend-links'),
  createFriendLink: (data: any) => api.post('/v1/admin/friend-links', data),
  updateFriendLink: (id: number, data: any) => api.put(`/v1/admin/friend-links/${id}`, data),
  deleteFriendLink: (id: number) => api.delete(`/v1/admin/friend-links/${id}`),
  getSiteConfig: () => api.get('/v1/admin/site-config'),
  saveSiteConfig: (data: any) => api.put('/v1/admin/site-config', data),
  upload: (file: File) => { const fd = new FormData(); fd.append('file', file); return api.post('/v1/admin/upload', fd) },
}
