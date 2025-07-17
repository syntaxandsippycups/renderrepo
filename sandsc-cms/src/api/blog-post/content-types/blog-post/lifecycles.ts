import { sendNewPostEmail } from '../../../../utils/email';

export default {
  async afterCreate(event) {
    const { result } = event;

    const subscribers = await strapi.entityService.findMany(
      'api::subscriber.subscriber' as any,
      {
        fields: ['email'],
      }
    );

    const subscribersTyped = subscribers as unknown as { email: string }[];

    for (const sub of subscribersTyped) {
      if (sub.email) {
        await sendNewPostEmail(sub.email, result.title);
      }
    }
  },
};
