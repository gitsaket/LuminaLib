"use client";

import { useRef, useState } from "react";
import { Upload, X } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button, Input } from "@/components/ui";
import { booksService } from "@/services/books.service";
import { toast } from "sonner";

interface UploadBookFormProps {
  onClose: () => void;
}

export function UploadBookForm({ onClose }: UploadBookFormProps) {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [form, setForm] = useState({
    title: "",
    author: "",
    isbn: "",
    description: "",
    genre: "",
    published_year: "",
  });

  const mutation = useMutation({
    mutationFn: () =>
      booksService.create({
        ...form,
        published_year: form.published_year ? Number(form.published_year) : undefined,
        file: selectedFile!,
      }),
    onSuccess: () => {
      toast.success("Book uploaded! AI summary is being generated.");
      qc.invalidateQueries({ queryKey: ["books"] });
      onClose();
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? "Upload failed"),
  });

  const field = (key: keyof typeof form) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value })),
  });

  const canSubmit = form.title && form.author && selectedFile;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm" onClick={onClose}>
      <div className="card bg-white relative w-full max-w-lg p-6" onClick={(e) => e.stopPropagation()}>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Add Book to Library</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Title *" placeholder="Book title" {...field("title")} />
            <Input label="Author *" placeholder="Author name" {...field("author")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Genre" placeholder="e.g. Fiction" {...field("genre")} />
            <Input label="Year" type="number" placeholder="2024" {...field("published_year")} />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="input resize-none"
              rows={2}
              placeholder="Brief description…"
              {...field("description")}
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="text-sm font-medium text-gray-700">Book File * (.pdf or .txt)</label>
            <div
              className="mt-1 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 hover:border-indigo-400 hover:bg-indigo-50 transition-colors"
              onClick={() => fileRef.current?.click()}
            >
              {selectedFile ? (
                <div className="flex items-center gap-2 text-sm text-indigo-700">
                  <Upload className="h-4 w-4" />
                  {selectedFile.name}
                </div>
              ) : (
                <>
                  <Upload className="h-8 w-8 text-gray-400" />
                  <p className="mt-1 text-sm text-gray-500">Click to select PDF or text file</p>
                </>
              )}
              <input
                ref={fileRef}
                type="file"
                className="hidden"
                accept=".pdf,.txt,text/plain,application/pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={() => mutation.mutate()} isLoading={mutation.isPending} disabled={!canSubmit}>
            Upload Book
          </Button>
        </div>
      </div>
    </div>
  );
}
