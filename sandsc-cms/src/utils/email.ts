export const sendNewPostEmail = async (email: string, title: string) => {
  await strapi.plugin('email').service('email').send({
    to: email,
    subject: `New Blog Post: ${title}`,
    text: `Check out our latest blog post titled "${title}".`,
  });
};
