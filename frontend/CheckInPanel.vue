<template>
	<div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
		<h2 class="text-lg font-bold text-gray-900">
			{{ __("Hey, {0} 👋", [employee?.data?.first_name]) }}
		</h2>

		<template v-if="settings.data?.allow_employee_checkin_from_mobile_app">
			<div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
				<span>{{ __("Last {0} was at {1}", [__(lastLogType), formatTimestamp(lastLog.time)]) }}</span>
				<span class="whitespace-pre"> &middot; </span>
				<router-link :to="{ name: 'EmployeeCheckinListView' }" v-slot="{ navigate }">
					<span @click="navigate" class="underline">View List</span>
				</router-link>
			</div>
			<Button
				class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
				id="open-checkin-modal"
				@click="handleEmployeeCheckin"
			>
				<template #prefix>
					<FeatherIcon
						:name="nextAction.action === 'IN' ? 'arrow-right-circle' : 'arrow-left-circle'"
						class="w-4"
					/>
				</template>
				{{ nextAction.label }}
			</Button>
		</template>

		<div v-else class="font-medium text-sm text-gray-500 mt-1.5">
			{{ dayjs().format("ddd, D MMMM, YYYY") }}
		</div>
	</div>

	<ion-modal
		v-if="settings.data?.allow_employee_checkin_from_mobile_app"
		ref="modal"
		trigger="open-checkin-modal"
		:initial-breakpoint="1"
		:breakpoints="[0, 1]"
	>
		<div class="h-120 w-full flex flex-col items-center justify-center gap-5 p-4 mb-5">
			<div class="flex flex-col gap-1.5 mt-2 items-center justify-center">
				<div class="font-bold text-xl">
					{{ dayjs(checkinTimestamp).format("hh:mm:ss a") }}
				</div>
				<div class="font-medium text-gray-500 text-sm">
					{{ dayjs().format("D MMM, YYYY") }}
				</div>
			</div>

			<template v-if="settings.data?.allow_geolocation_tracking">
				<span v-if="locationStatus" class="font-medium text-gray-500 text-sm">
					{{ locationStatus }}
				</span>
				<div class="rounded border-4 translate-z-0 block overflow-hidden w-full h-170">
					<iframe
						width="100%"
						height="170"
						frameborder="0"
						scrolling="no"
						marginheight="0"
						marginwidth="0"
						style="border: 0"
						:src="`https://maps.google.com/maps?q=${latitude},${longitude}&hl=en&z=15&amp;output=embed`"
					>
					</iframe>
				</div>
			</template>

			<!-- ======= PHOTO STEP ======= -->
			<div class="w-full flex flex-col gap-3">
				<div v-if="photoStep === 'capture'" class="w-full flex flex-col gap-3">
					<video
						ref="videoEl"
						autoplay
						playsinline
						muted
						class="w-full rounded-lg object-cover"
						style="max-height: 220px"
					></video>
					<p v-if="cameraError" class="text-red-500 text-sm text-center">{{ cameraError }}</p>
					<Button variant="solid" class="w-full py-5 text-sm" @click="capturePhoto">
						<template #prefix><FeatherIcon name="camera" class="w-4" /></template>
						{{ __("Take Photo") }}
					</Button>
				</div>

				<div v-else-if="photoStep === 'preview'" class="w-full flex flex-col gap-3">
					<img :src="photoDataUrl" class="w-full rounded-lg object-cover" style="max-height: 220px" />
					<div class="flex gap-2">
						<Button variant="outline" class="flex-1 py-5 text-sm" @click="retakePhoto">
							<template #prefix><FeatherIcon name="refresh-cw" class="w-4" /></template>
							{{ __("Retake") }}
						</Button>
						<Button
							:loading="checkins.insert.loading"
							variant="solid"
							class="flex-1 py-5 text-sm"
							@click="submitLog(nextAction.action)"
						>
							{{ __("Confirm {0}", [nextAction.label]) }}
						</Button>
					</div>
				</div>
			</div>
			<!-- ======= END PHOTO STEP ======= -->
		</div>
	</ion-modal>
</template>

<script setup>
import { createListResource, toast, FeatherIcon } from "frappe-ui"
import { computed, inject, ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import { IonModal, modalController } from "@ionic/vue"

import { formatTimestamp } from "@/utils/formatters"
import { settings } from "@/data/settings"

const DOCTYPE = "Employee Checkin"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const __ = inject("$translate")
const checkinTimestamp = ref(null)
const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")

// ---- Photo state ----
const photoStep = ref("capture")
const photoDataUrl = ref(null)
const cameraError = ref("")
const videoEl = ref(null)
let stream = null

const checkins = createListResource({
	doctype: DOCTYPE,
	fields: ["name", "employee", "employee_name", "log_type", "time", "device_id"],
	filters: { employee: employee.data.name },
	orderBy: "time desc",
})
checkins.reload()

const lastLog = computed(() => {
	if (checkins.list.loading || !checkins.data) return {}
	return checkins.data[0]
})

const lastLogType = computed(() => {
	return lastLog?.value?.log_type === "IN" ? "check-in" : "check-out"
})

const nextAction = computed(() => {
	return lastLog?.value?.log_type === "IN"
		? { action: "OUT", label: __("Check Out") }
		: { action: "IN", label: __("Check In") }
})

function handleLocationSuccess(position) {
	latitude.value = position.coords.latitude
	longitude.value = position.coords.longitude
	locationStatus.value = [
		__("Latitude: {0}°", [Number(latitude.value).toFixed(5)]),
		__("Longitude: {0}°", [Number(longitude.value).toFixed(5)]),
	].join(", ")
}

function handleLocationError(error) {
	locationStatus.value = "Unable to retrieve your location"
	if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
	if (!navigator.geolocation) {
		locationStatus.value = __("Geolocation is not supported by your current browser")
	} else {
		locationStatus.value = __("Locating...")
		navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError)
	}
}

async function startCamera() {
	cameraError.value = ""
	photoStep.value = "capture"
	photoDataUrl.value = null

	if (!navigator.mediaDevices?.getUserMedia) {
		cameraError.value = __("Camera is not supported on this device or browser.")
		return
	}

	try {
		stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: "user" },
			audio: false,
		})
		await nextTick()
		if (videoEl.value) {
			videoEl.value.srcObject = stream
		}
	} catch (err) {
		if (err.name === "NotAllowedError") {
			cameraError.value = __("Camera permission denied. Please allow camera access and try again.")
		} else if (err.name === "NotFoundError") {
			cameraError.value = __("No camera found on this device.")
		} else {
			cameraError.value = __("Camera error: {0}", [err.message])
		}
	}
}

function stopCamera() {
	if (stream) {
		stream.getTracks().forEach((t) => t.stop())
		stream = null
	}
}

function capturePhoto() {
	if (!videoEl.value) return

	const canvas = document.createElement("canvas")
	canvas.width = videoEl.value.videoWidth
	canvas.height = videoEl.value.videoHeight
	canvas.getContext("2d").drawImage(videoEl.value, 0, 0)

	let quality = 0.85
	let dataUrl = canvas.toDataURL("image/jpeg", quality)
	while (dataUrl.length > 1_000_000 && quality > 0.3) {
		quality -= 0.1
		dataUrl = canvas.toDataURL("image/jpeg", quality)
	}

	photoDataUrl.value = dataUrl
	photoStep.value = "preview"
	stopCamera()
}

function retakePhoto() {
	photoDataUrl.value = null
	startCamera()
}

const handleEmployeeCheckin = () => {
	checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
	if (settings.data?.allow_geolocation_tracking) fetchLocation()
	setTimeout(startCamera, 400)
}

async function dataUrlToFile(dataUrl, filename) {
	const res = await fetch(dataUrl)
	const blob = await res.blob()
	return new File([blob], filename, { type: "image/jpeg" })
}

const submitLog = async (logType) => {
	if (!photoDataUrl.value) {
		toast({
			title: __("Photo Required"),
			text: __("Please take a selfie before checking in."),
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
		return
	}

	const actionLabel = logType === "IN" ? __("Check-in") : __("Check-out")

	let photoUrl = null
	try {
		const file = await dataUrlToFile(
			photoDataUrl.value,
			`checkin_${employee.data.name}_${Date.now()}.jpg`
		)
		const formData = new FormData()
		formData.append("file", file)
		formData.append("is_private", "1")
		formData.append("doctype", DOCTYPE)

		const uploadRes = await fetch("/api/method/frappe.handler.upload_file", {
			method: "POST",
			headers: {
				"X-Frappe-CSRF-Token": frappe.csrf_token,
				"X-Requested-With": "XMLHttpRequest",
			},
			body: formData,
		})

		const uploadData = await uploadRes.json()
		photoUrl = uploadData.message?.file_url
		if (!photoUrl) throw new Error("No file_url in response")

	} catch (err) {
		toast({
			title: __("Upload Failed"),
			text: err.message,
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
		return
	}

	checkins.insert.submit(
		{
			employee: employee.data.name,
			log_type: logType,
			time: checkinTimestamp.value,
			latitude: latitude.value,
			longitude: longitude.value,
			custom_employee_photo: photoUrl,
		},
		{
			onSuccess() {
				stopCamera()
				modalController.dismiss()
				toast({
					title: __("Success"),
					text: __("{0} successful!", [actionLabel]),
					icon: "check-circle",
					position: "bottom-center",
					iconClasses: "text-green-500",
				})
			},
			onError(error) {
				let messages = error.messages || []
				for (const message of messages) {
					toast({
						title: __("Error"),
						text: message || __("{0} failed!", [actionLabel]),
						icon: "alert-circle",
						position: "bottom-center",
						iconClasses: "text-red-500",
					})
				}
			},
		}
	)
}

onMounted(() => {
	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype == DOCTYPE) checkins.reload()
	})
})

onBeforeUnmount(() => {
	stopCamera()
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")
})
</script>