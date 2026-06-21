const { getList } = require('./api-data');

function normalizeMetric(value, unit = '') {
  if (value === undefined || value === null || value === '') {
    return '--';
  }

  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) {
    return `${value}${unit}`;
  }

  return `${Math.round(numberValue)}${unit}`;
}

function isEnvironmentDevice(device = {}) {
  const type = `${device.device_type || ''}`.toLowerCase();
  const id = `${device.device_id || ''}`.toUpperCase();

  return type.includes('environment') || type.includes('env') || id.startsWith('ENV_');
}

function buildLatestMap(rows) {
  const latestByDevice = {};

  rows.forEach((row) => {
    if (!row || !row.device_id) {
      return;
    }

    const current = latestByDevice[row.device_id];
    const rowTime = row.sensor_time || row.received_at || '';
    const currentTime = current ? (current.sensor_time || current.received_at || '') : '';

    if (!current || rowTime >= currentTime) {
      latestByDevice[row.device_id] = row;
    }
  });

  return latestByDevice;
}

function getRecordTime(row = {}) {
  return row.sensor_time || row.received_at || row.create_time || '';
}

function sortByTimeDesc(rows) {
  return rows.slice().sort((a, b) => {
    const aTime = getRecordTime(a);
    const bTime = getRecordTime(b);
    return bTime.localeCompare(aTime);
  });
}

function mergeRealtimeData(devices, skinPayload, environmentPayload) {
  const skinRows = sortByTimeDesc(getList(skinPayload, ['skinData', 'skin_data', 'records']));
  const environmentRows = sortByTimeDesc(getList(environmentPayload, ['environmentData', 'environment_data', 'records']));
  const latestSkinByDevice = buildLatestMap(skinRows);
  const latestEnvironmentByDevice = buildLatestMap(environmentRows);

  return devices.map((device) => {
    const isEnvironment = isEnvironmentDevice(device);
    const latestSkin = latestSkinByDevice[device.device_id] || {};
    const latestEnvironment = latestEnvironmentByDevice[device.device_id] || {};

    if (isEnvironment) {
      return {
        ...device,
        isEnvironment: true,
        primaryLabel: '温度',
        primaryValue: normalizeMetric(device.temperature !== undefined ? device.temperature : latestEnvironment.temperature, '°C'),
        secondaryLabel: '湿度',
        secondaryValue: normalizeMetric(device.humidity !== undefined ? device.humidity : latestEnvironment.humidity, '%'),
        thirdLabel: 'PM2.5',
        thirdValue: normalizeMetric(device.pm25 !== undefined ? device.pm25 : latestEnvironment.pm25),
        fourthLabel: 'CO2',
        fourthValue: normalizeMetric(device.co2 !== undefined ? device.co2 : latestEnvironment.co2)
      };
    }

    return {
      ...device,
      isEnvironment: false,
      primaryLabel: '水分',
      primaryValue: normalizeMetric(device.last_moisture !== undefined ? device.last_moisture : latestSkin.moisture, '%'),
      secondaryLabel: '油性',
      secondaryValue: normalizeMetric(device.last_oiliness !== undefined ? device.last_oiliness : latestSkin.oiliness),
      thirdLabel: '电量',
      thirdValue: normalizeMetric(device.battery_level !== undefined ? device.battery_level : 100, '%'),
      fourthLabel: '位置',
      fourthValue: device.location || '未设置',
      last_moisture: normalizeMetric(device.last_moisture !== undefined ? device.last_moisture : latestSkin.moisture),
      last_oiliness: normalizeMetric(device.last_oiliness !== undefined ? device.last_oiliness : latestSkin.oiliness)
    };
  });
}

module.exports = {
  isEnvironmentDevice,
  mergeRealtimeData,
  sortByTimeDesc
};
