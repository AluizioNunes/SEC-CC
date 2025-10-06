import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type UserDocument = User & Document;

@Schema({ collection: 'user_preferences' })
export class User {
  @Prop({ required: true })
  userId: string;

  @Prop({ type: Object, default: {} })
  preferences: Record<string, any>;

  @Prop({ default: Date.now })
  created_at: Date;
}

export const UserSchema = SchemaFactory.createForClass(User);
