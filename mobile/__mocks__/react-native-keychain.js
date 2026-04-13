// In-memory storage for testing
const memoryStorage = {};

const mockKeychain = {
  setGenericPassword: async function(username, password, options) {
    memoryStorage[username] = password;
  },
  getGenericPassword: async function(options) {
    const key = options.service.split('.')[1];
    const value = memoryStorage[key];
    if (value) {
      return { username: key, password: value };
    }
    return false;
  },
  resetGenericPassword: async function(options) {
    const key = options.service.split('.')[1];
    delete memoryStorage[key];
  },
};

module.exports = mockKeychain;
module.exports.default = mockKeychain;