function getList(payload, keys = []) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (!payload || typeof payload !== 'object') {
    return [];
  }

  if (Array.isArray(payload.items)) {
    return payload.items;
  }

  if (Array.isArray(payload.data)) {
    return payload.data;
  }

  for (let i = 0; i < keys.length; i += 1) {
    const value = payload[keys[i]];
    if (Array.isArray(value)) {
      return value;
    }
  }

  return [];
}

function getTotal(payload, keys = []) {
  if (!payload || typeof payload !== 'object') {
    return Array.isArray(payload) ? payload.length : 0;
  }

  if (typeof payload.total === 'number') {
    return payload.total;
  }

  return getList(payload, keys).length;
}

function getPages(payload, pageSize, keys = []) {
  if (payload && typeof payload.pages === 'number') {
    return payload.pages;
  }

  const total = getTotal(payload, keys);
  return Math.max(1, Math.ceil(total / pageSize));
}

module.exports = {
  getList,
  getTotal,
  getPages
};
