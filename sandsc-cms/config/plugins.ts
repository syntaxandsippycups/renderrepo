export default ({ env }) => ({
  email: {
    config: {
      provider: 'nodemailer', // or use sendgrid/mailgun/etc
      providerOptions: {
        service: 'gmail',
        host: env('SMTP_HOST'),
        port: env.int('SMTP_PORT'),
        auth: {
          user: env('SMTP_USERNAME'),
          pass: env('SMTP_PASSWORD'),
        },
        secure: true,
      },
      settings: {
        defaultFrom: env('SMTP_FROM'),
        defaultReplyTo: env('SMTP_REPLYTO'),
      },
    },
  },
});
