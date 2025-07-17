import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate({ result }) {
    try {
      const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber' as any);

      if (Array.isArray(subscribers)) {
        for (const sub of subscribers) {
          if (sub && typeof sub.email === 'string') {
            await sendNewPostEmail(
              sub.email,
              result.title,
              result.content,
              result.slug
            );
          }
        }
      }
    } catch (err) {
      strapi.log.error('Error sending blog post emails', err);
    }
  },
};
