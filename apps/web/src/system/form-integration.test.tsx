import { act, renderHook } from "@testing-library/react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { describe, expect, it } from "vitest"
import { z } from "zod"

const schema = z.object({ label: z.string().min(3) })

describe("future owner form integration", () => {
  it("resolves valid and invalid fields with the installed RHF/Zod adapter", async () => {
    const { result } = renderHook(() =>
      useForm<z.infer<typeof schema>>({
        resolver: zodResolver(schema),
        defaultValues: { label: "" },
      })
    )
    await act(async () => {
      expect(await result.current.trigger()).toBe(false)
    })
    await act(async () => {
      result.current.setValue("label", "paper")
      expect(await result.current.trigger()).toBe(true)
    })
  })
})
