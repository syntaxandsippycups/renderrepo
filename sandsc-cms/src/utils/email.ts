import nodemailer from 'nodemailer';

export const sendNewPostEmail = async (to: string, title: string) => {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.SMTP_USERNAME,
      pass: process.env.SMTP_PASSWORD,
    },
  });

  await transporter.sendMail({
    from: `"Syntax and SuppyCups" <${process.env.EMAIL_USER}>`,
    to,
    subject: 'New Blog Post Published!',
    text: `Check out our latest post: "${title}"`,
    html: `<p>Check out our latest post: <strong>${title}</strong></p>`,
  });
};
