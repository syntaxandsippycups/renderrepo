import nodemailer from 'nodemailer';

export const sendNewPostEmail = async (
  to: string,
  title: string,
  content: string,
  slug: string,
  thumbnailUrl?: string
  subscriberId?: number // <-- new
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
  const unsubscribeUrl = `https://syntaxandsippycups.com/unsubscribe/${subscriberId}`; // <-- HERE


  const thumbnailHTML = thumbnailUrl
    ? `<img src="${thumbnailUrl}" alt="Blog Thumbnail" style="max-width: 100%; height: auto; margin-top: 10px;" />`
    : '';

  await transporter.sendMail({
    from: `"Syntax & SippyCups" <${process.env.EMAIL_USER}>`,
    to,
    subject: `New Blog Post: ${title}`,
    text: `Check out my latest post "${title}":\n\n${snippet}\n\nRead more: ${postUrl}`,
    html: `
        <div style="font-family: Arial, sans-serif; padding: 20px;">
          <h2>New Blog Post: ${title}</h2>
          ${thumbnailHTML}
          <p>${snippet}</p>
          <p><a href="${postUrl}" target="_blank">Read the full post</a></p>
          <hr style="margin: 30px 0;" />
          <p style="font-size: 0.9em; color: #888;">
            Don’t want to receive these emails?
            <a href="${unsubscribeUrl}" style="color: #555;">Unsubscribe here</a>.
          </p>
        </div>
      `,
  });
};
