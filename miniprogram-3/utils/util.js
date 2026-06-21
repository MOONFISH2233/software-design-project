const requestUtils = require('./request');

function formatNumber(n) {
  const value = n.toString();
  return value[1] ? value : `0${value}`;
}

function formatTime(date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = date.getHours();
  const minute = date.getMinutes();
  const second = date.getSeconds();

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`;
}

module.exports = {
  ...requestUtils,
  formatTime
};
