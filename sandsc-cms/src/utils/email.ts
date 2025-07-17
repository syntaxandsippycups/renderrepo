import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

export const sendNewPostEmail = async (to: string, postTitle: string) => {
  const info = await transporter.sendMail({
    from: `"Syntax & Sippy Cups" <${process.env.EMAIL_USER}>`,
    to,
    subject: `New blog post: ${postTitle}`,
    html: `<p>Hey there!</p><p>We've just published a new blog post titled <strong>${postTitle}</strong>. Check it out!</p>`,
  });

  console.log('Email sent:', info.messageId);
};
