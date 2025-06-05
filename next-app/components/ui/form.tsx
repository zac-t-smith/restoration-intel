/**
 * Form Component
 *
 * A collection of components for building forms with react-hook-form
 */

import * as React from "react";
import { useFormContext, FieldPath, FieldValues, Controller, UseControllerProps } from "react-hook-form";
import { cn } from "@/lib/utils";

interface FormProps<T extends FieldValues> extends React.FormHTMLAttributes<HTMLFormElement> {
  form: any; // Using any here to avoid complex typing in a simple component
}

const Form = <T extends FieldValues>({
  form,
  className,
  children,
  ...props
}: FormProps<T>) => {
  return (
    <form className={cn("space-y-6", className)} {...props}>
      {children}
    </form>
  );
};

interface FormFieldProps<T extends FieldValues> {
  name: FieldPath<T>;
  control?: any;
  defaultValue?: any;
  rules?: any;
  shouldUnregister?: boolean;
  children: React.ReactNode;
}

const FormField = <T extends FieldValues>({
  name,
  control,
  defaultValue,
  rules,
  shouldUnregister,
  children,
}: FormFieldProps<T>) => {
  return (
    <Controller
      name={name}
      control={control}
      defaultValue={defaultValue}
      rules={rules}
      shouldUnregister={shouldUnregister}
      render={({ field, fieldState }) => (
        <FormItemContext.Provider value={{ id: field.name, name: field.name, formItemId: `${field.name}-form-item`, formDescriptionId: `${field.name}-form-item-description`, formMessageId: `${field.name}-form-item-message`, ...field, ...fieldState }}>
          {children}
        </FormItemContext.Provider>
      )}
    />
  );
};

type FormItemContextValue = {
  id: string;
  name: string;
  formItemId: string;
  formDescriptionId: string;
  formMessageId: string;
  value?: any;
  onChange?: (...event: any[]) => void;
  onBlur?: () => void;
  ref?: React.RefObject<any>;
  error?: {
    type: string;
    message?: string;
  };
  isDirty: boolean;
  isTouched: boolean;
};

const FormItemContext = React.createContext<FormItemContextValue>({} as FormItemContextValue);

const useFormField = () => {
  const context = React.useContext(FormItemContext);
  if (!context) {
    throw new Error("useFormField must be used within a FormField");
  }
  return context;
};

interface FormItemProps extends React.HTMLAttributes<HTMLDivElement> {}

const FormItem = React.forwardRef<HTMLDivElement, FormItemProps>(
  ({ className, ...props }, ref) => {
    const id = React.useId();
    return (
      <div
        ref={ref}
        className={cn("space-y-2", className)}
        {...props}
      />
    );
  }
);
FormItem.displayName = "FormItem";

interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {}

const FormLabel = React.forwardRef<HTMLLabelElement, FormLabelProps>(
  ({ className, ...props }, ref) => {
    const { error, formItemId } = useFormField();
    return (
      <label
        ref={ref}
        className={cn(
          "text-sm font-medium text-gray-900",
          error && "text-red-500",
          className
        )}
        htmlFor={formItemId}
        {...props}
      />
    );
  }
);
FormLabel.displayName = "FormLabel";

interface FormControlProps extends React.HTMLAttributes<HTMLDivElement> {}

const FormControl = React.forwardRef<
  HTMLDivElement,
  FormControlProps
>(({ ...props }, ref) => {
  const { id, formItemId, formDescriptionId, formMessageId } = useFormField();
  return (
    <div
      ref={ref}
      id={formItemId}
      aria-describedby={
        !props.children
          ? `${formDescriptionId} ${formMessageId}`
          : undefined
      }
      aria-invalid={!!props.children}
      {...props}
    />
  );
});
FormControl.displayName = "FormControl";

interface FormDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

const FormDescription = React.forwardRef<
  HTMLParagraphElement,
  FormDescriptionProps
>(({ className, ...props }, ref) => {
  const { formDescriptionId } = useFormField();
  return (
    <p
      ref={ref}
      id={formDescriptionId}
      className={cn("text-sm text-gray-500", className)}
      {...props}
    />
  );
});
FormDescription.displayName = "FormDescription";

interface FormMessageProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children?: React.ReactNode;
}

const FormMessage = React.forwardRef<HTMLParagraphElement, FormMessageProps>(
  ({ className, children, ...props }, ref) => {
    const { error, formMessageId } = useFormField();
    const body = error ? String(error?.message) : children;

    if (!body) {
      return null;
    }

    return (
      <p
        ref={ref}
        id={formMessageId}
        className={cn("text-sm font-medium text-red-500", className)}
        {...props}
      >
        {body}
      </p>
    );
  }
);
FormMessage.displayName = "FormMessage";

export {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  useFormField,
};