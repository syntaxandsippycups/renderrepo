import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate({ result }) {
    try {
      const fullPost = result as any; // loosen type enforcement

      const title = fullPost.Title;
      const content = fullPost.content;
      const slug = fullPost.slug;
      const thumbnailUrl = fullPost.thumbnail?.url
        ? `https://api.syntaxandsippycups.com${fullPost.thumbnail.url}`
        : undefined;

      const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber' as any);

      if (Array.isArray(subscribers)) {
        for (const sub of subscribers) {
          if (sub && typeof sub.email === 'string') {
            await sendNewPostEmail(
              sub.email,
              title,
              content,
              slug,
              thumbnailUrl,
              String(sub.id) // <-- cast to string
            );
          }
        }
      }
    } catch (err) {
      strapi.log.error('Error sending blog post emails', err);
    }
  },
};
