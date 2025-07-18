export default ({ env }) => ({
  email: {
    config: {
      provider: 'nodemailer',
      providerOptions: {
        host: env('SMTP_HOST', 'smtp.gmail.com'), // Gmail's SMTP
        port: env.int('SMTP_PORT', 587),          // Use 587 (STARTTLS) for Gmail
        secure: false,                            // secure: false for STARTTLS (true is for port 465)
        auth: {
          user: env('SMTP_USERNAME'),
          pass: env('SMTP_PASSWORD'),
        },
      },
      settings: {
        defaultFrom: env('SMTP_FROM'),
        defaultReplyTo: env('SMTP_REPLYTO'),
      },
    },
  },
  upload: {
    config: {
      provider: 'cloudinary',
      providerOptions: {
        cloud_name: env('CLOUDINARY_NAME'),
        api_key: env('CLOUDINARY_KEY'),
        api_secret: env('CLOUDINARY_SECRET'),
        upload: {
          folder: 'strapi-media', // optional default folder
        },
      },
    },
  },
});
