import nodemailer from 'nodemailer';

export const sendNewPostEmail = async (
  to: string,
  title: string,
  content: string,
  slug: string
) => {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.SMTP_USERNAME,
      pass: process.env.SMTP_PASSWORD,
    },
  });

  const snippet = content.length > 200 ? content.slice(0, 200) + '...' : content;
  const postUrl = `https://syntaxandsippycups.com/blog/${slug}`;

  await transporter.sendMail({
    from: `"Syntax & SippyCups" <${process.env.EMAIL_USER}>`,
    to,
    subject: `New Blog Post: ${title}`,
    text: `Check out our new post "${title}":\n\n${snippet}\n\nRead more: ${postUrl}`,
    html: `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>New Blog Post: ${title}</h2>
        <p>${snippet}</p>
        <p><a href="${postUrl}" target="_blank">Read the full post</a></p>
      </div>
    `,
  });
};
