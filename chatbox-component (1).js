// chatbox.js
class FormCheckChatbox {
  constructor(containerSelector) {
    this.container = document.querySelector(containerSelector);
    if (!this.container) {
      console.error('Container not found:', containerSelector);
      return;
    }
    
    this.messages = [];
    this.init();
  }

  init() {
    // Create chatbox structure
    this.container.innerHTML = `
      <div class="chatbox-wrapper">
        <div class="chatbox-header">
          <h3>Exercise Form Checker</h3>
        </div>
        <div class="chatbox-messages" id="chat-messages"></div>
        <div class="chatbox-input-area">
          <div class="upload-container">
            <button class="upload-video-btn">Upload Video</button>
            <input type="file" id="video-upload" accept="video/*" style="display: none;">
            <div class="video-preview-container" style="display: none;"></div>
          </div>
          <div class="message-container">
            <textarea id="user-message" placeholder="Describe your exercise or ask for feedback..."></textarea>
            <button class="send-message-btn">Send</button>
          </div>
        </div>
      </div>
    `;
    
    // Add event listeners
    this.messageContainer = this.container.querySelector('#chat-messages');
    this.videoUploadBtn = this.container.querySelector('.upload-video-btn');
    this.videoInput = this.container.querySelector('#video-upload');
    this.videoPreviewContainer = this.container.querySelector('.video-preview-container');
    this.userMessageInput = this.container.querySelector('#user-message');
    this.sendMessageBtn = this.container.querySelector('.send-message-btn');
    
    this.videoUploadBtn.addEventListener('click', () => this.videoInput.click());
    this.videoInput.addEventListener('change', (e) => this.handleVideoUpload(e));
    this.sendMessageBtn.addEventListener('click', () => this.sendMessage());
    this.userMessageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // Add welcome message
    this.addBotMessage("Hi! I'm your exercise form checker. Upload a video of your exercise, and I'll provide feedback to help improve your form.");
  }
  
  handleVideoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Clear previous preview
    this.videoPreviewContainer.innerHTML = '';
    
    // Create video preview
    const video = document.createElement('video');
    video.controls = true;
    video.style.maxWidth = '100%';
    video.style.maxHeight = '200px';
    
    const source = document.createElement('source');
    source.src = URL.createObjectURL(file);
    source.type = file.type;
    
    video.appendChild(source);
    this.videoPreviewContainer.appendChild(video);
    this.videoPreviewContainer.style.display = 'block';
    
    // Add message about uploaded video
    this.addUserMessage(`Uploaded: ${file.name}`);
    this.addBotMessage("I've received your video! What exercise are you performing so I can check your form?");
  }
  
  sendMessage() {
    const message = this.userMessageInput.value.trim();
    if (!message) return;
    
    this.addUserMessage(message);
    this.userMessageInput.value = '';
    
    // Process the message and respond
    this.processUserMessage(message);
  }
  
  addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message user-message';
    messageEl.innerHTML = `<p>${message}</p>`;
    this.messageContainer.appendChild(messageEl);
    this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    this.messages.push({ role: 'user', content: message });
  }
  
  addBotMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message bot-message';
    messageEl.innerHTML = `<p>${message}</p>`;
    this.messageContainer.appendChild(messageEl);
    this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    this.messages.push({ role: 'bot', content: message });
  }
  
  processUserMessage(message) {
    // Check if there's a video uploaded
    const hasVideo = this.videoPreviewContainer.children.length > 0;
    
    // Simple rule-based responses for demo purposes
    // In a real implementation, you would integrate with a form-checking AI model
    const lowerMessage = message.toLowerCase();
    
    if (!hasVideo && !lowerMessage.includes('help') && !lowerMessage.includes('hi') && !lowerMessage.includes('hello')) {
      this.addBotMessage("Please upload a video of your exercise so I can provide specific feedback on your form.");
      return;
    }
    
    if (lowerMessage.includes('squat')) {
      this.addBotMessage("Based on your squat video, here are some form tips:\n\n1. Ensure your knees track over your toes but don't go past them\n2. Keep your back neutral - not rounded or excessively arched\n3. Go below parallel if your mobility allows\n4. Distribute weight through your heels and midfoot");
    } else if (lowerMessage.includes('deadlift')) {
      this.addBotMessage("Looking at your deadlift, here's my feedback:\n\n1. Keep the bar close to your body throughout the movement\n2. Engage your lats before lifting\n3. Hinge at the hips - this is a hip hinge, not a squat\n4. Maintain a neutral spine position\n5. Stand fully upright at the top of the movement");
    } else if (lowerMessage.includes('push up') || lowerMessage.includes('pushup')) {
      this.addBotMessage("Reviewing your push-up form:\n\n1. Keep your body in a straight line from head to heels\n2. Position hands about shoulder-width apart\n3. Lower your chest all the way to the floor\n4. Keep elbows at about a 45° angle to your body - not flared out");
    } else if (lowerMessage.includes('help') || lowerMessage.includes('exercises')) {
      this.addBotMessage("I can help with form checks for many exercises including squats, deadlifts, bench press, push-ups, pull-ups, lunges, and more! Just upload a video and let me know which exercise you're performing.");
    } else {
      this.addBotMessage("I'm analyzing your form. For more specific feedback, please tell me which exercise you're performing (e.g., squat, deadlift, push-up, etc.)");
    }
  }
}

// Export the class for use in other files
window.FormCheckChatbox = FormCheckChatbox;
