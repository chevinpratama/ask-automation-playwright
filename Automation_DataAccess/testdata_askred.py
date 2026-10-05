testcase_data = {
    "Akseptasi_RegistrasiDJP": {
        "reg_id": "REG-01",
        "module_name": "Akseptasi",
        "fitur": "Pembuatan Polis Asuransi",
        "severity": "High",
        "testcase_id": "TC-1",
        "testcase_name": "Pembuatan Polis Askred Regis DJP dengan Nomor PKS",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. User akses dengan credential yang valid\n"
            "2. Data PKS sudah tersedia dan valid untuk digunakan dalam proses registrasi\n"
        ),
        "expected_result": "Sistem berhasil membuat Polis Askred dengan PKS dan data tersimpan di ACS.",
        "actual_result": "Polis Askred dengan PKS berhasil dibuat dan tercatat di sistem ACS. No Request Number : {request_number}, No Polis: {polis}"
    },
    "Akseptasi_NotaPenawaran_RegistrasiDJP": {
        "reg_id": "REG-01",
        "module_name": "Akseptasi",
        "fitur": "Pembuatan Polis Asuransi",
        "severity": "High",
        "testcase_id": "TC-1.1",
        "testcase_name": "Pembuatan Polis Askred Regis DJP dengan Nota Penawaran",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. User akses dengan credential yang valid\n"
        ),
        "expected_result": "Sistem berhasil membuat Polis Askred dengan Nota Penawaran dan data tersimpan di ACS.",
        "actual_result": "Polis Askred dengan Nota Penawaran berhasil dibuat dan tercatat di sistem ACS."
    },
    "endorsement_nonfinancial": {
        "reg_id": "REG-01",
        "module_name": "Endorsement",
        "fitur": "Perubahan Data Polis (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-1.2",
        "testcase_name": "Endorse dengan jenis Non Financial pada data polis yang sudah terbit",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. User akses dengan credential yang valid\n"
            "2. Data Polis sudah terbit\n"
        ),
        "expected_result": "Sistem berhasil endorse Polis Askred jenis non financial dan data tersimpan di ACS.",
        "actual_result": "Polis Askred berhasil di endorse dan tercatat di sistem ACS."
    },
    "endorsement_financial": {
        "reg_id": "REG-01",
        "module_name": "Endorsement",
        "fitur": "Perubahan Data Polis (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-1.3",
        "testcase_name": "Endorse dengan jenis Financial pada data polis yang sudah terbit",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. User akses dengan credential yang valid\n"
            "2. Data Polis sudah terbit\n"
        ),
        "expected_result": "Sistem berhasil endorse Polis Askred jenis financial dan data tersimpan di ACS.",
        "actual_result": "Polis Askred berhasil di endorse dan tercatat di sistem ACS."
    },
    "endorsement_Pembatalan_perlunasandipercepat": {
        "reg_id": "REG-01",
        "module_name": "Endorsement",
        "fitur": "Perubahan Data Polis (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-1.4",
        "testcase_name": "Endorse dengan jenis Pembatalan perlunasan dipercepat pada data polis yang sudah terbit",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. Polis berhasil dibuat atau sudah terbit\n"
        ),
        "expected_result": "Sistem berhasil endorse Pembatalan Polis yang sudah terbit dan data tersimpan di ACS.",
        "actual_result": "Polis Askred berhasil dibatalkan dan tercatat di sistem ACS."
    },

    "endorsement_pembatalan_pertanggungan": {
        "reg_id": "REG-01",
        "module_name": "Endorsement",
        "fitur": "Perubahan Data Polis (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-1.5",
        "testcase_name": "Endorse dengan jenis Pembatalan pertanggungan pada data polis yang sudah terbit",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. Polis berhasil dibuat atau sudah terbit\n"
        ),
        "expected_result": "Sistem berhasil endorse Pembatalan Polis yang sudah terbit dan data tersimpan di ACS.",
        "actual_result": "Polis Askred berhasil dibatalkan dan tercatat di sistem ACS."
    },

    "endorsement_pembatalan_diluar_ketentuan": {
        "reg_id": "REG-01",
        "module_name": "Endorsement",
        "fitur": "Perubahan Data Polis (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-1.6",
        "testcase_name": "Endorse dengan jenis Pembatalan pertanggungan diluar ketentuan pada data polis yang sudah terbit",
        "jenis_test": "Positive",
        "tester_name": "Fathurrahman Al Farizi",
        "precondition": (
            "1. Polis berhasil dibuat atau sudah terbit\n"
        ),
        "expected_result": "Sistem berhasil endorse Pembatalan Polis yang sudah terbit dan data tersimpan di ACS.",
        "actual_result": "Polis Askred berhasil dibatalkan dan tercatat di sistem ACS."
    },
    # -------Klaim Askred-----------------#

    "Registrasi_Klaim_Disetujui": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Pengajuan Klaim karena Risiko yang Dijamin",
        "severity": "High",
        "testcase_id": "TC-2",
        "testcase_name": "Pengajuan Klaim dengan Polis Terbit",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis tersedia dan valid untuk pengajuan klaim\n"
            "3. User memiliki akses ke menu Klaim Askred\n"
        ),
        "expected_result": "Sistem menampilkan data klaim dengan status dokumen 'Setuju/Approved' dan data tercatat di sistem ACS sesuai registrasi.",
        "actual_result": "Data klaim berhasil ditemukan, No Klaim: {no_registrasi} dan No LPK: {no_lpk}, status dokumen muncul sebagai 'Setuju/Approved', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },

    "Klaim_KurangBayar": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Perubahan Data Klaim (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-2.1",
        "testcase_name": "Pengajuan klaim endorsement kurang bayar dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis sudah pernah diajukan klaim sampai disetujui\n"
            "3. Klaimnya memiliki data klaim yang valid untuk pengajuan endorsement kurang bayar\n"
        ),
        "expected_result": "Sistem menampilkan data klaim Kurang Bayar dengan status dokumen 'Setuju/Approved' dan data tercatat di sistem ACS sesuai registrasi.",
        "actual_result": "Data klaim berhasil ditemukan, No Klaim: {no_registrasi} dan No LPK berubah menjadi: {no_lpk_endorsement} setelah di endorsement, status dokumen muncul sebagai 'Setuju/Approved', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },

    "Klaim_LebihBayar": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Perubahan Data Klaim (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-2.2",
        "testcase_name": "Pengajuan klaim endorsement lebih bayar dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis sudah pernah diajukan klaim sampai disetujui\n"
            "3. Klaimnya memiliki data klaim yang valid untuk pengajuan endorsement lebih bayar\n"
        ),
        "expected_result": "Sistem menampilkan data klaim Lebih Bayar dengan status dokumen 'Setuju/Approved' dan data tercatat di sistem ACS sesuai registrasi.",
        "actual_result": "Data klaim berhasil ditemukan, No Klaim: {no_registrasi} dan No LPK berubah menjadi: {no_lpk_endorsement} setelah di endorsement, status dokumen muncul sebagai 'Setuju/Approved', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },

    "Klaim_Pembatalan": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Perubahan Data Klaim (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-2.3",
        "testcase_name": "Pengajuan klaim endorsement pembatalan dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis sudah pernah diajukan klaim sampai disetujui\n"
            "3. Klaimnya memiliki data klaim yang valid untuk pengajuan endorsement pembatalan\n"
        ),
        "expected_result": "Sistem menampilkan data klaim pembatalan dengan status dokumen 'Batal Klaim' dan data tercatat di sistem ACS sesuai registrasi.",
        "actual_result": "Data klaim berhasil ditemukan, No Klaim: {no_registrasi} dan No LPK berubah menjadi: {no_lpk_endorsement} setelah di endorsement, status dokumen muncul sebagai 'Batal Klaim', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai. "
    },

    "Klaim_SanggahBanding": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Perubahan Data Klaim (Endorsement)",
        "severity": "High",
        "testcase_id": "TC-2.4",
        "testcase_name": "Pengajuan klaim endorsement sanggah banding dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis sudah pernah diajukan klaim namun ditolak\n"
            "3. Klaimnya memiliki data klaim yang valid untuk pengajuan endorsement sanggah banding\n"
        ),
        "expected_result": "Sistem menampilkan data klaim Sanggah Banding dengan status dokumen 'Setuju/Approved' dan data tercatat di sistem ACS sesuai registrasi.",
        "actual_result": "Data klaim berhasil ditemukan, No Klaim: {no_registrasi} dan No LPK berubah menjadi: {no_lpk_endorsement} setelah di endorsement, status dokumen muncul sebagai 'Setuju/Approved', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },
    "Registrasi_Klaim_Ditolak": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Pengajuan Klaim karena Risiko yang Dijamin",
        "severity": "High",
        "testcase_id": "TC-2.5",
        "testcase_name": "Pengajuan klaim dengan kolektibilitas 3 (minimum kolektibilitas klaim 5)",
        "jenis_test": "Negative",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. User memiliki akses ke menu Klaim Askred\n"
            "3. Kolektibilitas klaim yang akan diajukan adalah 3, yang tidak memenuhi syarat minimum kolektibilitas 5 untuk pengajuan klaim\n"
        ),
        "expected_result": "Sistem menolak pengajuan klaim karena kolektibilitas belum memenuhi syarat (minimum 5) dan status klaim menjadi 'Tolak/Dropped'.",
        "actual_result": "Data klaim berhasil diproses. No KLaim: {no_registrasi}, status dokumen menjadi 'Tolak/Dropped', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },

    "Registrasi_Klaim_Dikembalikan": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Pengajuan Klaim karena Risiko yang Dijamin",
        "severity": "High",
        "testcase_id": "TC-2.6",
        "testcase_name": "Pengajuan klaim dengan resiko klaim yang tidak dicover = kebakaran (resiko yang dicover = kredit macet sesuai dengan PKS)",
        "jenis_test": "Negative",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. User memiliki akses ke menu Klaim Askred\n"
            "3. resiko klaim yang akan diajukan tidak sesuai dengan resiko yang dicover di PKS\n"
        ),
        "expected_result": "Sistem mengembalikan klaim kepada user karena risiko tidak sesuai dengan coverage PKS, dengan status dokumen 'Dikembalikan'.",
        "actual_result": "Data klaim berhasil diproses. No KLaim: {no_registrasi}, status dokumen menjadi 'Dikembalikan', dan tercatat di sistem ACS dengan nomor registrasi yang sesuai."
    },

    "Klaim_Lunas": {
        "reg_id": "REG-02",
        "module_name": "Klaim",
        "fitur": "Pengajuan Klaim karena Risiko yang Dijamin",
        "severity": "High",
        "testcase_id": "TC-2.7",
        "testcase_name": "Pelunasan klaim di FMS dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Polis sudah berhasil diterbitkan melalui proses Registrasi DJP\n"
            "2. Nomor polis sudah pernah diajukan klaim sampai disetujui\n"
            "3. Klaimnya memiliki data klaim yang valid untuk proses pelunasan di FMS\n"
        ),
        "expected_result": "Sistem berhasil memproses pelunasan klaim melalui portal FMS.",
        "actual_result": "Data klaim berhasil ditemukan dan pelunasan klaim berhasil dilakukan melalui portal FMS. No Klaim: {no_registrasi}, No Lpk: {no_lpk}, No Nota: {nomor_nota} dan No Jurnal Perlunasan: {nomor_jurnal_bbk}"
    },

    "Entry_Recovery_Tanpa_Perlimpahan": {
        "reg_id": "REG-03",
        "module_name": "Subrogasi",
        "fitur": "Proses Recovery Klaim",
        "severity": "High",
        "testcase_id": "TC-3",
        "testcase_name": "Proses recovery subrogasi dengan data klaim valid",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Klaim sudah berhasil diajukan dan disetujui\n"
            "2. Klaim sudah dilakukan pelunasan di FMS\n"
            "3. User memiliki akses ke menu Subrogasi Askred\n"
        ),
        "expected_result": "Sistem berhasil memproses recovery; saldo hak subrogasi otomatis berkurang dan nilai recovery bertambah sesuai yang diinput",
        "actual_result": "Proses recovery selesai dengan sukses; saldo hak subrogasi ter-update dan nilai recovery meningkat sesuai transaksi yang dilakukan. Saldo Hak Subrogasi sebelum recovery: {saldo_hak_subrogasi_before}, Nilai Recovery sebelum recovery: {saldo_recovery_before}, Nilai Recovery yang diinput: {nilai_penerima_recovery}, Saldo Hak Subrogasi setelah recovery: {saldo_hak_subrogasi_after}, Nilai Recovery setelah recovery: {saldo_recovery_after}"
    },

    "Inquiry_Hak_Subrogasi": {
        "reg_id": "REG-03",
        "module_name": "Subrogasi",
        "fitur": "Pencarian dan Monitoring Data Subrogasi",
        "severity": "High",
        "testcase_id": "TC-3.1",
        "testcase_name": "Inquiry hak subrogasi dengan data klaim yang sudah direcovery",
        "jenis_test": "Positive",
        "tester_name": "Chevin Rifan Pratama",
        "precondition": (
            "1. Klaim sudah dibayar (status paid)\n"
            "2. Proses recovery terhadap klaim sudah dilakukan dengan nominal valid\n"
            "3. Data klaim tersedia dan dapat diakses pada menu Inquiry Hak Subrogasi\n"
        ),
        "expected_result": "Nilai Recovery bertambah sesuai nominal input, dan saldo Hak Subrogasi berkurang secara otomatis dengan nilai yang sesuai setelah proses recovery dilakukan",
        "actual_result": "Nilai Recovery dan saldo Hak Subrogasi berhasil ter-update di sistem; nilai Recovery bertambah dan saldo Hak Subrogasi berkurang sesuai dengan nominal yang diinput"
    }
}
