/**
 * Settings module for the AI Call Secretary web interface.
 * Handles the settings page functionality.
 */

// Global state for settings
const settingsState = {
  general: {},
  voice: {},
  llm: {},
  telephony: {},
  api: {},
  user: {}
};

// Initialize settings page
function initSettingsPage() {
  // Set up settings navigation
  setupSettingsNav();
  
  // Load settings
  loadSettings();
  
  // Set up form submissions
  setupSettingsForms();
}

// Set up settings navigation
function setupSettingsNav() {
  const settingsNav = document.querySelectorAll('.settings-nav a');
  
  settingsNav.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Remove active class from all links
      settingsNav.forEach(navLink => {
        navLink.classList.remove('active');
      });
      
      // Hide all panels
      document.querySelectorAll('.settings-panel').forEach(panel => {
        panel.classList.remove('active');
      });
      
      // Add active class to clicked link
      link.classList.add('active');
      
      // Show corresponding panel
      const panelId = link.getAttribute('href').substring(1);
      document.getElementById(panelId).classList.add('active');
    });
  });
}

// Load settings
function loadSettings() {
  // Show loading state
  document.querySelectorAll('.settings-panel').forEach(panel => {
    panel.classList.add('loading');
  });
  
  // Fetch settings
  api.getSettings()
    .then(settings => {
      settingsState.general = settings.general || {};
      settingsState.voice = settings.voice || {};
      settingsState.llm = settings.llm || {};
      settingsState.telephony = settings.telephony || {};
      settingsState.api = settings.api || {};
      settingsState.user = settings.user || {};
      
      // Populate forms
      populateGeneralSettings();
      populateVoiceSettings();
      populateLLMSettings();
      populateTelephonySettings();
      populateAPISettings();
      populateUserSettings();
      
      // Remove loading state
      document.querySelectorAll('.settings-panel').forEach(panel => {
        panel.classList.remove('loading');
      });
    })
    .catch(error => {
      console.error('Error loading settings:', error);
      showNotification('Error loading settings', 'error');
      
      // Remove loading state
      document.querySelectorAll('.settings-panel').forEach(panel => {
        panel.classList.remove('loading');
      });
    });
}

// Set up settings forms
function setupSettingsForms() {
  // General settings form
  const generalForm = document.getElementById('general-settings-form');
  if (generalForm) {
    generalForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveGeneralSettings();
    });
    
    generalForm.addEventListener('reset', () => {
      populateGeneralSettings();
    });
  }
  
  // Voice settings form
  const voiceForm = document.getElementById('voice-settings-form');
  if (voiceForm) {
    voiceForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveVoiceSettings();
    });
    
    voiceForm.addEventListener('reset', () => {
      populateVoiceSettings();
    });
  }
  
  // LLM settings form
  const llmForm = document.getElementById('llm-settings-form');
  if (llmForm) {
    llmForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveLLMSettings();
    });
    
    llmForm.addEventListener('reset', () => {
      populateLLMSettings();
    });
  }
  
  // Telephony settings form
  const telephonyForm = document.getElementById('telephony-settings-form');
  if (telephonyForm) {
    telephonyForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveTelephonySettings();
    });
    
    telephonyForm.addEventListener('reset', () => {
      populateTelephonySettings();
    });
  }
  
  // API settings form
  const apiForm = document.getElementById('api-settings-form');
  if (apiForm) {
    apiForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveAPISettings();
    });
    
    apiForm.addEventListener('reset', () => {
      populateAPISettings();
    });
  }
  
  // User settings form
  const userForm = document.getElementById('user-settings-form');
  if (userForm) {
    userForm.addEventListener('submit', (e) => {
      e.preventDefault();
      saveUserSettings();
    });
    
    userForm.addEventListener('reset', () => {
      populateUserSettings();
    });
  }
}

// Populate general settings form
function populateGeneralSettings() {
  const form = document.getElementById('general-settings-form');
  const settings = settingsState.general;
  
  // Business name
  const businessNameInput = form.querySelector('[name="business_name"]');
  if (businessNameInput && settings.business_name) {
    businessNameInput.value = settings.business_name;
  }
  
  // Business hours
  if (settings.business_hours) {
    const hoursContainer = form.querySelector('.hours-container');
    if (hoursContainer) {
      hoursContainer.innerHTML = '';
      
      const daysOfWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
      const dayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      
      daysOfWeek.forEach((day, index) => {
        const dayHours = settings.business_hours[day] || { start: '09:00', end: '17:00' };
        
        const dayContainer = document.createElement('div');
        dayContainer.className = 'day-hours';
        dayContainer.innerHTML = `
          <label>${dayLabels[index]}</label>
          <div class="time-range">
            <input type="time" name="${day}_start" value="${dayHours.start}">
            <span>to</span>
            <input type="time" name="${day}_end" value="${dayHours.end}">
          </div>
        `;
        
        hoursContainer.appendChild(dayContainer);
      });
    }
  }
  
  // Additional general settings can be added here
}

// Save general settings
function saveGeneralSettings() {
  const form = document.getElementById('general-settings-form');
  const formData = new FormData(form);
  
  // Extract and structure data
  const generalSettings = {
    business_name: formData.get('business_name'),
    business_hours: {
      monday: { start: formData.get('monday_start'), end: formData.get('monday_end') },
      tuesday: { start: formData.get('tuesday_start'), end: formData.get('tuesday_end') },
      wednesday: { start: formData.get('wednesday_start'), end: formData.get('wednesday_end') },
      thursday: { start: formData.get('thursday_start'), end: formData.get('thursday_end') },
      friday: { start: formData.get('friday_start'), end: formData.get('friday_end') },
      saturday: { start: formData.get('saturday_start'), end: formData.get('saturday_end') },
      sunday: { start: formData.get('sunday_start'), end: formData.get('sunday_end') }
    }
  };
  
  // Save settings
  api.updateSettings('general', generalSettings)
    .then(() => {
      showNotification('General settings saved successfully', 'success');
      // Update local state
      settingsState.general = generalSettings;
    })
    .catch(error => {
      console.error('Error saving general settings:', error);
      showNotification('Error saving general settings', 'error');
    });
}

// Populate voice settings form
function populateVoiceSettings() {
  const form = document.getElementById('voice-settings-form');
  const settings = settingsState.voice;
  
  // Build voice settings form content if it's empty
  if (form.children.length <= 2) { // Just the form actions and error message
    form.insertAdjacentHTML('afterbegin', `
      <div class="form-group">
        <label for="voice-engine">Voice Engine</label>
        <select id="voice-engine" name="engine" required>
          <option value="elevenlabs">ElevenLabs</option>
          <option value="azure">Azure Text-to-Speech</option>
          <option value="google">Google Text-to-Speech</option>
          <option value="local">Local TTS</option>
        </select>
      </div>
      <div class="form-group">
        <label for="voice-id">Voice ID</label>
        <select id="voice-id" name="voice_id">
          <option value="">Loading voices...</option>
        </select>
      </div>
      <div class="form-group">
        <label for="voice-speed">Speaking Rate</label>
        <div class="range-input">
          <input type="range" id="voice-speed" name="speed" min="0.5" max="2" step="0.1" value="1">
          <span class="range-value">1.0</span>
        </div>
      </div>
      <div class="form-group">
        <label for="voice-pitch">Pitch</label>
        <div class="range-input">
          <input type="range" id="voice-pitch" name="pitch" min="-20" max="20" step="1" value="0">
          <span class="range-value">0</span>
        </div>
      </div>
      <div class="form-section">
        <h4>STT Settings</h4>
        <div class="form-group">
          <label for="stt-engine">Speech-to-Text Engine</label>
          <select id="stt-engine" name="stt_engine" required>
            <option value="google">Google Speech-to-Text</option>
            <option value="azure">Azure Speech-to-Text</option>
            <option value="whisper">OpenAI Whisper</option>
          </select>
        </div>
      </div>
    `);
    
    // Add event listeners for range inputs
    const rangeInputs = form.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
      const valueDisplay = input.nextElementSibling;
      valueDisplay.textContent = input.value;
      
      input.addEventListener('input', () => {
        valueDisplay.textContent = input.value;
      });
    });
    
    // Add event listener for voice engine change
    const engineSelect = form.querySelector('#voice-engine');
    engineSelect.addEventListener('change', () => {
      loadVoiceOptions(engineSelect.value);
    });
  }
  
  // Set values based on settings
  if (settings.engine) {
    form.querySelector('#voice-engine').value = settings.engine;
    loadVoiceOptions(settings.engine);
  }
  
  if (settings.voice_id) {
    const voiceSelect = form.querySelector('#voice-id');
    if (voiceSelect.querySelector(`option[value="${settings.voice_id}"]`)) {
      voiceSelect.value = settings.voice_id;
    }
  }
  
  if (settings.speed) {
    const speedInput = form.querySelector('#voice-speed');
    speedInput.value = settings.speed;
    speedInput.nextElementSibling.textContent = settings.speed;
  }
  
  if (settings.pitch) {
    const pitchInput = form.querySelector('#voice-pitch');
    pitchInput.value = settings.pitch;
    pitchInput.nextElementSibling.textContent = settings.pitch;
  }
  
  if (settings.stt_engine) {
    form.querySelector('#stt-engine').value = settings.stt_engine;
  }
}

// Load voice options based on selected engine
function loadVoiceOptions(engine) {
  const voiceSelect = document.getElementById('voice-id');
  
  // Show loading state
  voiceSelect.innerHTML = '<option value="">Loading voices...</option>';
  
  // Fetch voices for the selected engine
  api.getVoices(engine)
    .then(voices => {
      voiceSelect.innerHTML = '';
      
      voices.forEach(voice => {
        const option = document.createElement('option');
        option.value = voice.id;
        option.textContent = voice.name;
        voiceSelect.appendChild(option);
      });
      
      // Set current voice if available
      if (settingsState.voice.voice_id) {
        if (voiceSelect.querySelector(`option[value="${settingsState.voice.voice_id}"]`)) {
          voiceSelect.value = settingsState.voice.voice_id;
        }
      }
    })
    .catch(error => {
      console.error('Error loading voices:', error);
      voiceSelect.innerHTML = '<option value="">Error loading voices</option>';
    });
}

// Save voice settings
function saveVoiceSettings() {
  const form = document.getElementById('voice-settings-form');
  const formData = new FormData(form);
  
  // Extract and structure data
  const voiceSettings = {
    engine: formData.get('engine'),
    voice_id: formData.get('voice_id'),
    speed: parseFloat(formData.get('speed')),
    pitch: parseInt(formData.get('pitch')),
    stt_engine: formData.get('stt_engine')
  };
  
  // Save settings
  api.updateSettings('voice', voiceSettings)
    .then(() => {
      showNotification('Voice settings saved successfully', 'success');
      // Update local state
      settingsState.voice = voiceSettings;
    })
    .catch(error => {
      console.error('Error saving voice settings:', error);
      showNotification('Error saving voice settings', 'error');
    });
}

// Populate LLM settings form
function populateLLMSettings() {
  const form = document.getElementById('llm-settings-form');
  const settings = settingsState.llm;
  
  // Build LLM settings form content if it's empty
  if (form.children.length <= 2) { // Just the form actions and error message
    form.insertAdjacentHTML('afterbegin', `
      <div class="form-group">
        <label for="llm-provider">LLM Provider</label>
        <select id="llm-provider" name="provider" required>
          <option value="ollama">Ollama (Local)</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="azure">Azure OpenAI</option>
        </select>
      </div>
      <div class="form-group">
        <label for="llm-model">Model</label>
        <select id="llm-model" name="model">
          <option value="">Loading models...</option>
        </select>
      </div>
      <div class="form-group">
        <label for="llm-api-key">API Key</label>
        <input type="password" id="llm-api-key" name="api_key" placeholder="Enter API key">
      </div>
      <div class="form-group">
        <label for="llm-temperature">Temperature</label>
        <div class="range-input">
          <input type="range" id="llm-temperature" name="temperature" min="0" max="1" step="0.1" value="0.7">
          <span class="range-value">0.7</span>
        </div>
      </div>
      <div class="form-group">
        <label for="llm-context-window">Context Window</label>
        <select id="llm-context-window" name="context_window">
          <option value="2000">2000 tokens</option>
          <option value="4000">4000 tokens</option>
          <option value="8000">8000 tokens</option>
          <option value="16000">16000 tokens</option>
          <option value="32000">32000 tokens</option>
        </select>
      </div>
      <div class="form-group">
        <label>Context Modules</label>
        <div class="checkbox-group">
          <div class="checkbox-item">
            <input type="checkbox" id="context-business-info" name="context_modules" value="business_info">
            <label for="context-business-info">Business Information</label>
          </div>
          <div class="checkbox-item">
            <input type="checkbox" id="context-call-history" name="context_modules" value="call_history">
            <label for="context-call-history">Call History</label>
          </div>
          <div class="checkbox-item">
            <input type="checkbox" id="context-appointments" name="context_modules" value="appointments">
            <label for="context-appointments">Appointments</label>
          </div>
          <div class="checkbox-item">
            <input type="checkbox" id="context-faq" name="context_modules" value="faq">
            <label for="context-faq">FAQ</label>
          </div>
        </div>
      </div>
    `);
    
    // Add event listeners for range inputs
    const rangeInputs = form.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
      const valueDisplay = input.nextElementSibling;
      valueDisplay.textContent = input.value;
      
      input.addEventListener('input', () => {
        valueDisplay.textContent = input.value;
      });
    });
    
    // Add event listener for provider change
    const providerSelect = form.querySelector('#llm-provider');
    providerSelect.addEventListener('change', () => {
      loadModelOptions(providerSelect.value);
      
      // Show/hide API key field based on provider
      const apiKeyGroup = form.querySelector('#llm-api-key').closest('.form-group');
      if (providerSelect.value === 'ollama') {
        apiKeyGroup.style.display = 'none';
      } else {
        apiKeyGroup.style.display = 'block';
      }
    });
  }
  
  // Set values based on settings
  if (settings.provider) {
    const providerSelect = form.querySelector('#llm-provider');
    providerSelect.value = settings.provider;
    loadModelOptions(settings.provider);
    
    // Show/hide API key field based on provider
    const apiKeyGroup = form.querySelector('#llm-api-key').closest('.form-group');
    if (settings.provider === 'ollama') {
      apiKeyGroup.style.display = 'none';
    } else {
      apiKeyGroup.style.display = 'block';
    }
  }
  
  if (settings.model) {
    const modelSelect = form.querySelector('#llm-model');
    setTimeout(() => {
      if (modelSelect.querySelector(`option[value="${settings.model}"]`)) {
        modelSelect.value = settings.model;
      }
    }, 500); // Wait for models to load
  }
  
  if (settings.api_key) {
    form.querySelector('#llm-api-key').value = settings.api_key;
  }
  
  if (settings.temperature) {
    const tempInput = form.querySelector('#llm-temperature');
    tempInput.value = settings.temperature;
    tempInput.nextElementSibling.textContent = settings.temperature;
  }
  
  if (settings.context_window) {
    form.querySelector('#llm-context-window').value = settings.context_window;
  }
  
  if (settings.context_modules) {
    const checkboxes = form.querySelectorAll('input[name="context_modules"]');
    checkboxes.forEach(checkbox => {
      checkbox.checked = settings.context_modules.includes(checkbox.value);
    });
  }
}

// Load model options based on selected provider
function loadModelOptions(provider) {
  const modelSelect = document.getElementById('llm-model');
  
  // Show loading state
  modelSelect.innerHTML = '<option value="">Loading models...</option>';
  
  // Fetch models for the selected provider
  api.getModels(provider)
    .then(models => {
      modelSelect.innerHTML = '';
      
      models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.name;
        modelSelect.appendChild(option);
      });
      
      // Set current model if available
      if (settingsState.llm.model) {
        if (modelSelect.querySelector(`option[value="${settingsState.llm.model}"]`)) {
          modelSelect.value = settingsState.llm.model;
        }
      }
    })
    .catch(error => {
      console.error('Error loading models:', error);
      
      // Provide default options based on provider
      let defaultModels = [];
      
      switch (provider) {
        case 'ollama':
          defaultModels = [
            { id: 'llama2', name: 'Llama 2' },
            { id: 'mistral', name: 'Mistral' },
            { id: 'orca', name: 'Orca' }
          ];
          break;
        case 'openai':
          defaultModels = [
            { id: 'gpt-4', name: 'GPT-4' },
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
          ];
          break;
        case 'anthropic':
          defaultModels = [
            { id: 'claude-3-opus', name: 'Claude 3 Opus' },
            { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet' },
            { id: 'claude-3-haiku', name: 'Claude 3 Haiku' }
          ];
          break;
        case 'azure':
          defaultModels = [
            { id: 'gpt-4', name: 'GPT-4' },
            { id: 'gpt-35-turbo', name: 'GPT-3.5 Turbo' }
          ];
          break;
      }
      
      modelSelect.innerHTML = '';
      defaultModels.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.name;
        modelSelect.appendChild(option);
      });
      
      // Set current model if available
      if (settingsState.llm.model) {
        if (modelSelect.querySelector(`option[value="${settingsState.llm.model}"]`)) {
          modelSelect.value = settingsState.llm.model;
        }
      }
    });
}

// Save LLM settings
function saveLLMSettings() {
  const form = document.getElementById('llm-settings-form');
  const formData = new FormData(form);
  
  // Get selected context modules
  const contextModules = [];
  form.querySelectorAll('input[name="context_modules"]:checked').forEach(checkbox => {
    contextModules.push(checkbox.value);
  });
  
  // Extract and structure data
  const llmSettings = {
    provider: formData.get('provider'),
    model: formData.get('model'),
    api_key: formData.get('api_key'),
    temperature: parseFloat(formData.get('temperature')),
    context_window: parseInt(formData.get('context_window')),
    context_modules: contextModules
  };
  
  // Save settings
  api.updateSettings('llm', llmSettings)
    .then(() => {
      showNotification('LLM settings saved successfully', 'success');
      // Update local state
      settingsState.llm = llmSettings;
    })
    .catch(error => {
      console.error('Error saving LLM settings:', error);
      showNotification('Error saving LLM settings', 'error');
    });
}

// Populate telephony settings form
function populateTelephonySettings() {
  const form = document.getElementById('telephony-settings-form');
  const settings = settingsState.telephony;
  
  // Build telephony settings form content if it's empty
  if (form.children.length <= 2) { // Just the form actions and error message
    form.insertAdjacentHTML('afterbegin', `
      <div class="form-group">
        <label for="telephony-provider">Telephony Provider</label>
        <select id="telephony-provider" name="provider" required>
          <option value="freeswitch">FreeSWITCH</option>
          <option value="twilio">Twilio</option>
          <option value="asterisk">Asterisk</option>
        </select>
      </div>
      <div class="form-group">
        <label for="telephony-server">Server Address</label>
        <input type="text" id="telephony-server" name="server" placeholder="Enter server address">
      </div>
      <div class="form-group">
        <label for="telephony-port">Port</label>
        <input type="number" id="telephony-port" name="port" placeholder="Enter port number">
      </div>
      <div class="form-group">
        <label for="telephony-username">Username</label>
        <input type="text" id="telephony-username" name="username" placeholder="Enter username">
      </div>
      <div class="form-group">
        <label for="telephony-password">Password</label>
        <input type="password" id="telephony-password" name="password" placeholder="Enter password">
      </div>
      <div class="form-section">
        <h4>Call Handling</h4>
        <div class="form-group">
          <label for="greeting-message">Greeting Message</label>
          <textarea id="greeting-message" name="greeting_message" rows="3" placeholder="Enter greeting message"></textarea>
        </div>
        <div class="form-group">
          <label for="voicemail-message">Voicemail Message</label>
          <textarea id="voicemail-message" name="voicemail_message" rows="3" placeholder="Enter voicemail message"></textarea>
        </div>
        <div class="form-group">
          <label for="max-ring-time">Max Ring Time (seconds)</label>
          <input type="number" id="max-ring-time" name="max_ring_time" min="10" max="120" step="5">
        </div>
      </div>
    `);
  }
  
  // Set values based on settings
  if (settings.provider) {
    form.querySelector('#telephony-provider').value = settings.provider;
  }
  
  if (settings.server) {
    form.querySelector('#telephony-server').value = settings.server;
  }
  
  if (settings.port) {
    form.querySelector('#telephony-port').value = settings.port;
  }
  
  if (settings.username) {
    form.querySelector('#telephony-username').value = settings.username;
  }
  
  if (settings.password) {
    form.querySelector('#telephony-password').value = settings.password;
  }
  
  if (settings.greeting_message) {
    form.querySelector('#greeting-message').value = settings.greeting_message;
  }
  
  if (settings.voicemail_message) {
    form.querySelector('#voicemail-message').value = settings.voicemail_message;
  }
  
  if (settings.max_ring_time) {
    form.querySelector('#max-ring-time').value = settings.max_ring_time;
  }
}

// Save telephony settings
function saveTelephonySettings() {
  const form = document.getElementById('telephony-settings-form');
  const formData = new FormData(form);
  
  // Extract and structure data
  const telephonySettings = {
    provider: formData.get('provider'),
    server: formData.get('server'),
    port: parseInt(formData.get('port')),
    username: formData.get('username'),
    password: formData.get('password'),
    greeting_message: formData.get('greeting_message'),
    voicemail_message: formData.get('voicemail_message'),
    max_ring_time: parseInt(formData.get('max_ring_time'))
  };
  
  // Save settings
  api.updateSettings('telephony', telephonySettings)
    .then(() => {
      showNotification('Telephony settings saved successfully', 'success');
      // Update local state
      settingsState.telephony = telephonySettings;
    })
    .catch(error => {
      console.error('Error saving telephony settings:', error);
      showNotification('Error saving telephony settings', 'error');
    });
}

// Populate API settings form
function populateAPISettings() {
  const form = document.getElementById('api-settings-form');
  const settings = settingsState.api;
  
  // Build API settings form content if it's empty
  if (form.children.length <= 2) { // Just the form actions and error message
    form.insertAdjacentHTML('afterbegin', `
      <div class="form-group">
        <label for="api-host">API Host</label>
        <input type="text" id="api-host" name="host" placeholder="Enter API host">
      </div>
      <div class="form-group">
        <label for="api-port">API Port</label>
        <input type="number" id="api-port" name="port" placeholder="Enter API port">
      </div>
      <div class="form-group">
        <label for="api-debug">Debug Mode</label>
        <div class="toggle-switch">
          <input type="checkbox" id="api-debug" name="debug">
          <label for="api-debug"></label>
        </div>
      </div>
      <div class="form-section">
        <h4>Security</h4>
        <div class="form-group">
          <label for="api-secret-key">Secret Key</label>
          <input type="password" id="api-secret-key" name="secret_key" placeholder="Enter secret key">
        </div>
        <div class="form-group">
          <label for="api-token-expiry">Token Expiry (hours)</label>
          <input type="number" id="api-token-expiry" name="token_expiry" min="1" max="168">
        </div>
        <div class="form-group">
          <label for="api-cors-origins">CORS Allowed Origins</label>
          <input type="text" id="api-cors-origins" name="cors_origins" placeholder="Enter comma-separated origins">
        </div>
      </div>
    `);
  }
  
  // Set values based on settings
  if (settings.host) {
    form.querySelector('#api-host').value = settings.host;
  }
  
  if (settings.port) {
    form.querySelector('#api-port').value = settings.port;
  }
  
  if (settings.debug !== undefined) {
    form.querySelector('#api-debug').checked = settings.debug;
  }
  
  if (settings.secret_key) {
    form.querySelector('#api-secret-key').value = settings.secret_key;
  }
  
  if (settings.token_expiry) {
    form.querySelector('#api-token-expiry').value = settings.token_expiry;
  }
  
  if (settings.cors_origins) {
    form.querySelector('#api-cors-origins').value = settings.cors_origins.join(', ');
  }
}

// Save API settings
function saveAPISettings() {
  const form = document.getElementById('api-settings-form');
  const formData = new FormData(form);
  
  // Parse CORS origins
  const corsOrigins = formData.get('cors_origins')
    .split(',')
    .map(origin => origin.trim())
    .filter(origin => origin.length > 0);
  
  // Extract and structure data
  const apiSettings = {
    host: formData.get('host'),
    port: parseInt(formData.get('port')),
    debug: formData.get('debug') === 'on',
    secret_key: formData.get('secret_key'),
    token_expiry: parseInt(formData.get('token_expiry')),
    cors_origins: corsOrigins
  };
  
  // Save settings
  api.updateSettings('api', apiSettings)
    .then(() => {
      showNotification('API settings saved successfully', 'success');
      // Update local state
      settingsState.api = apiSettings;
    })
    .catch(error => {
      console.error('Error saving API settings:', error);
      showNotification('Error saving API settings', 'error');
    });
}

// Populate user settings form
function populateUserSettings() {
  const form = document.getElementById('user-settings-form');
  const settings = settingsState.user;
  
  // Build user settings form content if it's empty
  if (form.children.length <= 2) { // Just the form actions and error message
    form.insertAdjacentHTML('afterbegin', `
      <div class="form-group">
        <label for="user-username">Username</label>
        <input type="text" id="user-username" name="username" placeholder="Enter username" readonly>
      </div>
      <div class="form-group">
        <label for="user-full-name">Full Name</label>
        <input type="text" id="user-full-name" name="full_name" placeholder="Enter full name">
      </div>
      <div class="form-group">
        <label for="user-email">Email</label>
        <input type="email" id="user-email" name="email" placeholder="Enter email">
      </div>
      <div class="form-section">
        <h4>Change Password</h4>
        <div class="form-group">
          <label for="user-current-password">Current Password</label>
          <input type="password" id="user-current-password" name="current_password" placeholder="Enter current password">
        </div>
        <div class="form-group">
          <label for="user-new-password">New Password</label>
          <input type="password" id="user-new-password" name="new_password" placeholder="Enter new password">
        </div>
        <div class="form-group">
          <label for="user-confirm-password">Confirm New Password</label>
          <input type="password" id="user-confirm-password" name="confirm_password" placeholder="Confirm new password">
        </div>
      </div>
      <div class="form-section">
        <h4>Interface Settings</h4>
        <div class="form-group">
          <label for="user-theme">Theme</label>
          <select id="user-theme" name="theme">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System Default</option>
          </select>
        </div>
        <div class="form-group">
          <label for="user-language">Language</label>
          <select id="user-language" name="language">
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>
      </div>
    `);
  }
  
  // Set values based on settings
  if (settings.username) {
    form.querySelector('#user-username').value = settings.username;
  }
  
  if (settings.full_name) {
    form.querySelector('#user-full-name').value = settings.full_name;
  }
  
  if (settings.email) {
    form.querySelector('#user-email').value = settings.email;
  }
  
  if (settings.theme) {
    form.querySelector('#user-theme').value = settings.theme;
  }
  
  if (settings.language) {
    form.querySelector('#user-language').value = settings.language;
  }
  
  // Clear password fields
  form.querySelector('#user-current-password').value = '';
  form.querySelector('#user-new-password').value = '';
  form.querySelector('#user-confirm-password').value = '';
}

// Save user settings
function saveUserSettings() {
  const form = document.getElementById('user-settings-form');
  const formData = new FormData(form);
  
  // Validate password change if requested
  const currentPassword = formData.get('current_password');
  const newPassword = formData.get('new_password');
  const confirmPassword = formData.get('confirm_password');
  
  if (newPassword && newPassword !== confirmPassword) {
    showNotification('New passwords do not match', 'error');
    return;
  }
  
  // Extract and structure data
  const userSettings = {
    full_name: formData.get('full_name'),
    email: formData.get('email'),
    theme: formData.get('theme'),
    language: formData.get('language')
  };
  
  // Add password change if requested
  if (currentPassword && newPassword) {
    userSettings.current_password = currentPassword;
    userSettings.new_password = newPassword;
  }
  
  // Save settings
  api.updateUserSettings(userSettings)
    .then(() => {
      showNotification('User settings saved successfully', 'success');
      // Update local state (but not password fields)
      delete userSettings.current_password;
      delete userSettings.new_password;
      settingsState.user = {
        ...settingsState.user,
        ...userSettings
      };
      
      // Apply theme if changed
      applyTheme(userSettings.theme);
      
      // Clear password fields
      form.querySelector('#user-current-password').value = '';
      form.querySelector('#user-new-password').value = '';
      form.querySelector('#user-confirm-password').value = '';
    })
    .catch(error => {
      console.error('Error saving user settings:', error);
      showNotification('Error saving user settings', 'error');
    });
}

// Apply theme
function applyTheme(theme) {
  // Remove existing theme classes
  document.body.classList.remove('theme-light', 'theme-dark');
  
  if (theme === 'system') {
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.body.classList.add('theme-dark');
    } else {
      document.body.classList.add('theme-light');
    }
  } else {
    // Apply selected theme
    document.body.classList.add(`theme-${theme}`);
  }
}

// Function to load settings
function loadSettings() {
  // For demo purposes, we'll simulate a settings load
  setTimeout(() => {
    // Simulate API response
    const settings = {
      general: {
        business_name: 'AI Call Secretary Demo',
        business_hours: {
          monday: { start: '09:00', end: '17:00' },
          tuesday: { start: '09:00', end: '17:00' },
          wednesday: { start: '09:00', end: '17:00' },
          thursday: { start: '09:00', end: '17:00' },
          friday: { start: '09:00', end: '17:00' },
          saturday: { start: '10:00', end: '14:00' },
          sunday: { start: '00:00', end: '00:00' }
        }
      },
      voice: {
        engine: 'elevenlabs',
        voice_id: 'sample-voice',
        speed: 1.0,
        pitch: 0,
        stt_engine: 'whisper'
      },
      llm: {
        provider: 'ollama',
        model: 'llama2',
        temperature: 0.7,
        context_window: 4000,
        context_modules: ['business_info', 'call_history', 'appointments']
      },
      telephony: {
        provider: 'freeswitch',
        server: 'localhost',
        port: 8021,
        username: 'admin',
        password: '',
        greeting_message: 'Hello, thank you for calling. How may I assist you today?',
        voicemail_message: 'Sorry, we are unavailable at the moment. Please leave a message after the tone.',
        max_ring_time: 60
      },
      api: {
        host: 'localhost',
        port: 8080,
        debug: false,
        secret_key: '',
        token_expiry: 24,
        cors_origins: ['http://localhost:3000']
      },
      user: {
        username: 'admin',
        full_name: 'Administrator',
        email: 'admin@example.com',
        theme: 'light',
        language: 'en'
      }
    };
    
    // Update state
    settingsState.general = settings.general;
    settingsState.voice = settings.voice;
    settingsState.llm = settings.llm;
    settingsState.telephony = settings.telephony;
    settingsState.api = settings.api;
    settingsState.user = settings.user;
    
    // Populate forms
    populateGeneralSettings();
    populateVoiceSettings();
    populateLLMSettings();
    populateTelephonySettings();
    populateAPISettings();
    populateUserSettings();
    
    // Remove loading state
    document.querySelectorAll('.settings-panel').forEach(panel => {
      panel.classList.remove('loading');
    });
    
    // Apply current theme
    applyTheme(settings.user.theme);
  }, 500);
}